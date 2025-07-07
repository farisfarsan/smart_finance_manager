from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.db.models import Sum

from core.models import Invoice
import requests
import json
import tempfile
from datetime import datetime, timedelta
from collections import defaultdict


def home(request):
    return render(request, 'core/home.html')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            messages.success(request, "✅ Signup successful. Please login.")
            return redirect('login')
        else:
            messages.error(request, "❌ Signup failed. Please check your input.")
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def trigger_email_fetch(email_user, email_pass, user_id):
    try:
        payload = {
            "email_user": email_user,
            "email_pass": email_pass,
            "user_id": int(user_id)
        }
        response = requests.post("http://127.0.0.1:8001/fetch-invoices/", json=payload)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Fetch error: {e}")
    return None


def get_previous_month(month_str):
    current = datetime.strptime(month_str, "%B %Y")
    prev = (current.replace(day=1) - timedelta(days=1))
    return prev.strftime("%B %Y")


@login_required
def dashboard(request):
    invoices = []
    fetching = False

    if request.method == "POST":
        email_user = request.POST.get("email")
        email_pass = request.POST.get("password")
        fetching = True
        fetch_result = trigger_email_fetch(email_user, email_pass, request.user.id)
        if fetch_result and "invoices" in fetch_result:
            for inv in fetch_result["invoices"]:
                Invoice.objects.get_or_create(
                    user=request.user,
                    amount=inv.get("amount", 0.0),
                    platform=inv.get("platform", "Unknown"),
                    date_fetched=datetime.strptime(inv.get("date_fetched"), "%Y-%m-%d")
                )
            messages.success(request, "✅ Invoices fetched successfully.")
        else:
            messages.error(request, "❌ Invoice fetch failed.")

    invoices = Invoice.objects.filter(user=request.user)

    month_filter = request.GET.get("month", "")
    spend_by_date = defaultdict(float)
    month_spend = 0.0
    last_month_spend = 0.0

    for inv in invoices:
        date_str = inv.date_fetched.strftime("%Y-%m-%d")
        month_label = inv.date_fetched.strftime("%B %Y")
        amount = float(inv.amount)

        if not month_filter or month_label == month_filter:
            spend_by_date[date_str] += amount
            month_spend += amount
        elif month_label == get_previous_month(month_filter or datetime.today().strftime("%B %Y")):
            last_month_spend += amount

    chart_labels = list(spend_by_date.keys())
    chart_data = list(spend_by_date.values())

    smart_insight = ""
    if month_spend > last_month_spend:
        smart_insight = "⚠️ Your spend has increased compared to last month."
    elif month_spend < last_month_spend:
        smart_insight = "🎉 Great job! You spent less than last month."
    elif month_spend == 0:
        smart_insight = "🕵️ No spending recorded this month yet."

    used_months = set(inv.date_fetched.strftime("%B %Y") for inv in invoices)
    months = [{"label": m, "value": m} for m in sorted(used_months)]

    spend_diff = round(month_spend - last_month_spend, 2)
    percent_diff = round((spend_diff / last_month_spend * 100), 2) if last_month_spend else 0.0

    context = {
        "invoices": invoices,
        "fetching": fetching,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "month_filter": month_filter,
        "months": months,
        "smart_insight": smart_insight,
        "month_spend": round(month_spend, 2),
        "last_month_spend": round(last_month_spend, 2),
        "spend_diff": spend_diff,
        "percent_diff": percent_diff,
        "total_chart_spend": sum(chart_data),  # ✅ Added to support chart logic
    }

    return render(request, "core/dashboard.html", context)



@login_required
def download_pdf(request):
    invoices = Invoice.objects.filter(user=request.user)
    html_string = render_to_string("core/pdf_template.html", {
        'invoices': invoices,
        'user': request.user,
        'date': datetime.now()
    })

    from weasyprint import HTML
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp:
        HTML(string=html_string).write_pdf(temp.name)
        temp.seek(0)
        pdf_data = temp.read()

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=invoice_summary.pdf"
    return response


@login_required
def latest_spend_chart(request):
    today = datetime.today().date()
    past_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime('%a') for d in past_7_days]
    values = []

    for day in past_7_days:
        total = Invoice.objects.filter(user=request.user, date_fetched=day).aggregate(Sum('amount'))['amount__sum'] or 0
        values.append(total)

    return JsonResponse({"labels": labels, "values": values})


@csrf_exempt
def save_invoices(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            user_id = payload.get("user_id")
            invoices = payload.get("invoices", [])

            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)

            for inv in invoices:
                Invoice.objects.get_or_create(
                    user=user,
                    platform=inv.get("platform", "Unknown"),
                    amount=inv.get("amount", 0.0),
                    date_fetched=parse_date(inv.get("date_fetched"))
                )

            return JsonResponse({"message": "Invoices saved successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)
