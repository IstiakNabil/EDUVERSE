# earnings/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Earning, Withdrawal


@login_required
def earnings_view(request):
    # Handle withdrawal request
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            Withdrawal.objects.create(teacher=request.user, amount=amount)
            # Add a success message
            return redirect('earnings:earnings_page')

    # Calculate totals
    total_earnings = Earning.objects.filter(teacher=request.user).aggregate(total=Sum('amount'))['total'] or 0
    total_withdrawn = Withdrawal.objects.filter(teacher=request.user, status='approved').aggregate(total=Sum('amount'))[
                          'total'] or 0
    pending_withdrawal = \
    Withdrawal.objects.filter(teacher=request.user, status='pending').aggregate(total=Sum('amount'))['total'] or 0

    current_balance = total_earnings - total_withdrawn - pending_withdrawal

    # Get transaction history
    recent_earnings = Earning.objects.filter(teacher=request.user).order_by('-timestamp')[:10]
    withdrawal_history = Withdrawal.objects.filter(teacher=request.user).order_by('-requested_at')

    context = {
        'total_earnings': total_earnings,
        'total_withdrawn': total_withdrawn,
        'current_balance': current_balance,
        'pending_withdrawal': pending_withdrawal,
        'recent_earnings': recent_earnings,
        'withdrawal_history': withdrawal_history,
    }
    return render(request, 'earnings/earnings_page.html', context)