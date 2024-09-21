from django.shortcuts import render
from .models import Book, Member, Transaction
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from django.utils import timezone

# Create book
def create_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        isbn = request.POST['isbn']
        publisher = request.POST['publisher']
        page_count = request.POST['pagecount']
        available = request.POST['Available']

        # Create and save book
        Book.objects.create(title=title, authors=author, isbn=isbn, publisher=publisher, page_count=page_count, available=available)
        messages.success(request, "Book added successfully!")
        return redirect('book_list')
    
    return render(request, 'create_book.html')

# Update book
def update_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.title = request.POST['title']
        book.authors = request.POST['author']
        book.isbn = request.POST['isbn']
        book.page_count=request.POST['pagecount']
        book.available=request.POST['Available']
        # book.stock = request.POST['stock']
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect('book_list')

    return render(request, 'create_book.html', {'book': book})

# Delete book
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('book_list')

# List all books
def book_list(request):
    books = Book.objects.all()
    members = Member.objects.all()  # Get all members to use in the template
    transactions = Transaction.objects.all()  # Assuming this model exists
    

    return render(request, 'book_list.html', {'books': books, 'member': members,'transactions': transactions})

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Member

# View to display the member list
def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

# View to add or update a member
def create_member(request, member_id=None):
    if member_id:
        member = get_object_or_404(Member, id=member_id)
    else:
        member = None

    if request.method == 'POST':
        # Logic to save member goes here...
        # Example: member.name = request.POST['name']
        # member.save()
        return redirect('member_list')

    return render(request, 'create_member.html', {'member': member})

# View to delete a member
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'confirm_delete.html', {'member': member})


#--------------------------------------
# Issue a book to a member
def issue_book(request,book_id):
    book =Book.objects.get(id=book_id)
    members = Member.objects.all()
    if request.method == "POST":
        member =Member.objects.get(id=request.POST['member_id'])      
          
        # Check if the member has an outstanding debt greater than Rs. 500
        if member.outstanding_debt > 500:
            messages.error(request, "Member's outstanding debt exceeds Rs. 500. Cannot issue book.")
            return redirect('book_list')
    
        # Check if the book is available for issuing
        if book.available:
            book.available = False  # Mark the book as unavailable
            book.save()

            # Create a new transaction for this issuance
            Transaction.objects.create(book=book, member=member, issue_date=timezone.now())
            messages.success(request, f"Book '{book.title}' issued to {member.name} successfully!")
            return redirect('book_list')
        else:
            messages.error(request, f"Book '{book.title}' is not available for issuing.")
        
    return render(request,'issue_book.html',{"book":book,"members":members})


def calculate_rental_fee(transaction):
    borrowed_days = (timezone.now() - transaction.issue_date).days  # Both are timezone-aware now
    if borrowed_days > 14:  # Assuming a 14-day loan period
        overdue_days = borrowed_days - 14
        return overdue_days * 5  # Assuming Rs. 5/day fine
    return 0  # No fee if returned within 14 days

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Member, Transaction
from django.utils import timezone
from datetime import timedelta

from django.contrib import messages  # Import messages framework

def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    book = transaction.book
    member = transaction.member
    
    # Calculate rental fee (assume 14 days is the free limit)
    return_date = timezone.now()
    borrow_date = transaction.issue_date
    days_borrowed = (return_date - borrow_date).days
    rental_fee = 0
    if days_borrowed > 14:
        rental_fee = (days_borrowed - 14) * 50  # For example, charge $5 per extra day
    
    # Handle form submission
    if request.method == 'POST':
        # Mark the book as available and update transaction
        book.available = True
        book.save()

        transaction.return_date = return_date
        transaction.save()

        # Set a success message
        messages.success(request, f'Book "{book.title}" returned successfully. Rental fee: ₹{rental_fee}')
        
        # Redirect to the book list
        return redirect('book_list')
    
    # Pass the necessary data to the template
    context = {
        'book': book,
        'member': member,
        'rental_fee': rental_fee,
    }
    
    return render(request, 'return_book.html', context)



# Function to calculate rental fee


#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------

def search_books(request):
    query = request.GET.get('q')
    books = Book.objects.filter(Q(title__icontains=query) | Q(authors__icontains=query))
    return render(request, 'book_list.html', {'books': books})

# Import Books from Frappe API
def import_books(request, page=1, title=""):
    url = "https://frappe.io/api/method/frappe-library?page=2&title=and"
    params = {"page": page, "title": title}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        books = response.json()["message"]
        for book in books:
            Book.objects.create(
                title=book['title'],
                authors=book['authors'],
                isbn=book['isbn'],
                publisher=book['publisher'],
                page_count=book['  num_pages']
            )
        return JsonResponse({"status": "success", "imported_books": books})
    else:
        return JsonResponse({"status": "error", "message": "Failed to fetch data"})

