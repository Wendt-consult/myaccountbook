from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from collections import OrderedDict, defaultdict
from django.contrib import messages

from app.models.contacts_model import Contacts
from app.models.users_model import *
from app.models.products_model import *
from app.models.creditnote_model import *

from app.forms.products_form import * 
from app.forms.contact_forms import * 
from app.forms.tax_form import *
from app.forms.inc_fomsets import *

import string

from app.other_constants import creditnote_constant

from django.db.models import Q

import json, os, csv

from app.helpers import email_helper

from datetime import datetime

from django.conf import settings
#=====================================================================================
#   CREDIT_NOTE VIEW
#=====================================================================================
#

class CreditView(View):

    # Template 
    template_name = 'app/app_files/creditnote/base.html'
    
    # Initialize 
    data = defaultdict()
    data["view"] = ""
    data["contacts"] = {}
    data["active_link"] = 'Credit Note'
    data["breadcrumb_title"] = 'CREDIT NOTE'

    # Custom CSS/JS Files For Inclusion into template
    data["css_files"] = []
    data["js_files"] = []

    data["included_template"] = 'app/app_files/creditnote/view_creditnote.html'
    
    #
    #
    def get(self, request):        

        credit_note = CreditNode.objects.filter(user = request.user)
        self.data['credit_note'] = credit_note
        return render(request, self.template_name, self.data)

#=====================================================================================
#   ADD CREDITNOTE
#=====================================================================================
#
def add_creditnote(request, slug ):

    # Initialize 
    data = defaultdict()

    # Template 
    template_name = 'app/app_files/creditnote/add_creditnote.html'
    data["included_template"] = 'app/app_files/creditnote/add_creditnote.html'
    
    # Custom CSS/JS Files For Inclusion into template
    data["css_files"] = []
    data["js_files"] = ['custom_files/js/creditnote.js','custom_files/js/product.js','custom_files/js/contacts.js']

    # Set link as active in menubar
    data["active_link"] = 'Credit Note'
    data["breadcrumb_title"] = 'CREDIT NOTE'
    
    # Product form
    data["add_product_images_form"] = ProductPhotosForm()
    data["add_product_form"] = ProductForm(request.user) 

    # Initialize Forms
    data["contact_form"] = ContactsForm()
    data["tax_form"] = TaxForm()
    data["other_details_form"] = OtherDetailsForm()
    data["social_form"] = ContactsExtraForm()

    # FORMSETS    
    data["address_formset"] = AddressFormset
    data["accounts_formset"] = AccountsFormset


    # list contact name
    contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))
    
    default = Organisations.objects.filter(user = request.user)
    if(len(default) > 0):
        msg = default[0].terms_and_condition
        data['term_msg'] = msg
    data["contacts"] = contacts
    data["state"] = creditnote_constant.state
    data['tax'] = creditnote_constant.tax
    # list product name
    if( int(slug) == 1):
        products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
        name = []
        ids =[]
        count = len(products)
        for i in range(0,count):
            if(products[i].hsn_code is not None):
                a = str(products[i].product_name)+' - ('+str(products[i].hsn_code)+')'
                name.append(a)
            else:
                name.append(products[i].product_name)
            ids.append(products[i].id)
        data = {'products': name, 'ids': ids ,} 
        return JsonResponse(data)
    elif(int(slug) == 0):
        products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
        data["products"] = products
        return render(request, template_name, data)


#=====================================================================================
#   FETCH CONTACT
#=====================================================================================
#

def fetch_contact(request, slug):
     # Initialize 
    data = defaultdict()
    
    contacts = Contacts.objects.get(Q(user = request.user) & Q(pk = int(slug)))
    data['contacts'] =  contacts.email 
    data['address'] = []
    address = User_Address_Details.objects.filter(Q(contact = slug) & Q(is_billing_address = 1)).values('contact_person','flat_no', 'street', 'city', 'state', 'country', 'pincode')
    for i in range(0,len(address)):
        add=""
        for j in address[i].values():
            if( j is not None):
                add+=str(j)+', '
        data['address'].append(add[0:(len(add))-2])
    return JsonResponse(data)

#=====================================================================================
#   FETCH PRODUCT_type/Units/Price/Product Description/Currency
#=====================================================================================
#
def fetch_product(request, slug):
    
    # Initialize 
    data = defaultdict()
    products = ProductsModel.objects.get(pk = int(slug))
    data['product'] = products.product_type
    data['unit'] = products.get_unit_display()
    data['price'] =  products.selling_price
    data['desc'] = products.product_description
    return JsonResponse(data)

#=====================================================================================
#   CHECK CREDITNOTE UNIQUR AND SET DEFULT
#=====================================================================================
#

def unique_credit_number(request, ins, number):
    data = defaultdict()
    if(ins == 0):
        credit_note = CreditNode.objects.filter(user = request.user)

        count = len(credit_note)

        if(count == 0):
            data['credit_number'] = 'CN-1001'
        else:
            a = 'CN-100'+str(count+1)
            result = credit_note.filter(credit_number__iexact = a).exists()
            if(result == True):
                num = 'CN-100'+str(count+2)
                data['credit_number'] = num
            else:
                data['credit_number'] = a
        
        return JsonResponse(data)
    elif (ins == 1):
        # check credit note number is unquie
        credit_note = CreditNode.objects.filter(Q(user = request.user) & Q(credit_number = number))
        count = len(credit_note)
        if(count == 0):
            data['unique'] = 0
        else:
            data['unique'] = 1
        return JsonResponse(data)
#=====================================================================================
#   SAVE CREDIT_NOTE
#=====================================================================================
#

def save_credit_note(request):

    if request.POST:
        name = request.POST.get("customerName")
        email = request.POST.get("Email_Address")
        cc_email = request.POST.get("CC_Email_Address")
        address = request.POST.get("BillingAddress")
        creditnote_date = request.POST.get("CreditNoteDate")
        supply = request.POST.get("supplyPlace")
        invoice_reference = request.POST.get("Reference",'None')
        credit_number = request.POST.get("CreditNoteNumber",'None')
        term_condition = request.POST.get("t&c")
        message = request.POST.get("Message")
        
        attach_check = request.POST.get("attach_check", False)
                
        attachement = request.FILES.get("Attachment")
        
        creditnote_number = request.POST.get("creditnote_number_default",'off')
        # amount = request.POST.get("amo")
        # description = request.POST.get("description")
        subtotal = request.POST.get("SubTotal")
        cgst_5 = request.POST.get("CGST_5")
        sgst_5 = request.POST.get("SGST_5")
        igst_5 = request.POST.get("IGST_5")
        cgst_12 = request.POST.get("CGST_12")
        sgst_12 = request.POST.get("SGST_12")
        igst_12 = request.POST.get("IGST_12")
        cgst_18 = request.POST.get("CGST_18")
        sgst_18 = request.POST.get("SGST_18")
        igst_18 = request.POST.get("IGST_18")
        cgst_28 = request.POST.get("CGST_28")
        sgst_28 = request.POST.get("SGST_28")
        igst_28 = request.POST.get("IGST_28")
        cgst_other = request.POST.get("CGST_other")
        sgst_other = request.POST.get("SGST_other")
        igst_other = request.POST.get("IGST_other")
        total = request.POST.get("Total","None")
        default = request.POST.get('default','off')
        if(default == 'on'):
            org = Organisations.objects.get(user = request.user)
            if(org.terms_and_condition is None):
                org.terms_and_condition = term_condition
                org.save()
                # org2 = Organisations(user = request.user, terms_and_condition = term_condition)
                # org2.save()
            elif(org.terms_and_condition is not None):
                Organisations.objects.get(user = request.user).update(terms_and_condition = term_condition)
                

        if 'save_send' in request.POST:
            save_type = 1
        elif 'save_close' in request.POST:
            save_type = 2
        elif 'save_draft' in request.POST:
            save_type = 3

        contact = Contacts.objects.get(user = request.user, pk = int(name))

        credit = CreditNode(user= request.user, contact_name = contact,save_type = save_type,email=email,cc_email=cc_email,billing_address=address,credit_date=creditnote_date,
                 state_supply= supply,invoice_refrence=invoice_reference,credit_number=credit_number,creditnote_number_check=creditnote_number,terms_and_condition=term_condition,
                 Note=message,attachements=attachement,sub_total=subtotal,cgst_5 = cgst_5 ,igst_5 = igst_5,sgst_5 = sgst_5,cgst_12 = cgst_12,
                 igst_12 = igst_12,sgst_12 = sgst_12,cgst_18 = cgst_18,igst_18 = igst_18,sgst_18 = sgst_18,cgst_28 = cgst_28,
                 igst_28 = igst_28,sgst_28 = sgst_28,cgst_other=cgst_other,igst_other = igst_other,sgst_other = sgst_other,total=total)
        credit.save()               

        product_name = request.POST.getlist('ItemName[]',None)
        product_desc = request.POST.getlist('desc[]',None)
        product_type = request.POST.getlist('type[]',None)
        # product_currency = request.POST.getlist('currency[]',None)
        product_price = request.POST.getlist('Price[]',None)
        product_unit = request.POST.getlist('Unit[]',None)
        product_quantity = request.POST.getlist('Quantity[]',None)
        product_discount = request.POST.getlist('Discount[]',None)
        product_discount_type = request.POST.getlist('Dis[]',None)
        product_tax = request.POST.getlist('tax[]',None)
        product_amount = request.POST.getlist('Amount[]',None)

        count = len(product_name)
        for i in range(0,count):
            if(product_name[i] == '-------' ):
                products = None
                if(len(product_desc[i]) > 0 or len(product_amount[i]) > 0):
                    credit.amount = product_amount[i]
                    credit.description = product_desc[i]
                    credit.save()
            else:
                
                products = ProductsModel.objects.get(pk = int(product_name[i]))
                creditnote_item = creditnote_Items(user= request.user,credit_inventory= credit,product=products,description=product_desc[i],
                                        product_type=product_type[i],price=product_price[i],unit=product_unit[i],quantity=product_quantity[i],
                                        discount_type = product_discount_type[i],discount=product_discount[i],
                                        tax=product_tax[i],amount=product_amount[i])

                creditnote_item.save()   
        
        #
        # PDF CODE
        #

        #
        # EMAIL SENDING FUNCTION
        #
        
        if(save_type == 1):        
            if attach_check:
                credit_note_mailer(request, credit, contact, send_attachments = True)
            else:
                credit_note_mailer(request, credit, contact, send_attachments = False)
            
        
        return redirect('/creditnotes/', permanent = False)
    return redirect('/creditnotes/', permanent = False)

#=====================================================================================
#   LEASR_PRODUCT_FETCH
#=====================================================================================
#

def last_product_fetch(request):
    data = defaultdict()
    products = ProductsModel.objects.latest('pk')
    if(products.hsn_code is not None):
        data['name'] = str(products.product_name)+' - ('+str(products.hsn_code)+')'
    else:
        data['name'] = products.product_name
        
    data['ids'] = products.id
    
    # data = {'ids':products.id,'name':products.product_name}
    return JsonResponse(data)


#=====================================================================================
#   LEASR_CONTACT_FETCH
#=====================================================================================
#

def last_contact_fetch(request):
    contacts = Contacts.objects.latest('pk')
    # if(contacts.organization_name is not None):
    #     name = str()
    data = {'ids':contacts.id,'name':str(contacts)}
    return JsonResponse(data)

#=====================================================================================
#   EDIT CREDITNOTE 
#=====================================================================================
#
class EditCreditnote(View):

    # Template 
    template_name = 'app/app_files/creditnote/edit_creditnote.html'

    # Initialize 
    data = defaultdict()
    data["view"] = ""

    # Custom CSS/JS Files For Inclusion into template
    data["css_files"] = []
    data["js_files"] = ['custom_files/js/creditnote.js','custom_files/js/product.js','custom_files/js/contacts.js']
    data["active_link"] = 'Credit Note'
    data["breadcrumb_title"] = 'CREDIT NOTE'

    data["included_template"] = 'app/app_files/creditnote/edit_creditnote.html'

    # Initialize Forms
    data["contact_form"] = ContactsForm()
    data["tax_form"] = TaxForm()
    data["other_details_form"] = OtherDetailsForm()
    data["social_form"] = ContactsExtraForm()

    # FORMSETS    
    data["address_formset"] = AddressFormset
    data["accounts_formset"] = AccountsFormset

    def get(self, request, *args, **kwargs):

        try:
            creditnote = CreditNode.objects.get(pk = int(kwargs["ins"]))
            contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))

            # inactive and delete product or contact
            intcontacts = Contacts.objects.filter(Q(user = request.user))
            intproducts = ProductsModel.objects.filter(Q(user = request.user))
            
            products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
            creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
            default = Organisations.objects.filter(user = request.user)
        except:
            return redirect('/unauthorized/', permanent=False)

        self.data["contacts"] = contacts
        self.data["state"] = creditnote_constant.state
        self.data['tax'] = creditnote_constant.tax

        # inactive and delete product or contact
        self.data["intproducts"] = intproducts
        self.data["intcontacts"] = intcontacts

        self.data["products"] = products
        self.data["credit_note"] = creditnote
        self.data["creditnote_item"] = creditnote_item
        self.data["item_count"] = len(creditnote_item)-1

        # Product form
        self.data["add_product_images_form"] = ProductPhotosForm()
        self.data["add_product_form"] = ProductForm(request.user) 
        # msg = len(defult)
        if( len(default) > 0):
            msg = default[0].terms_and_condition
            self.data['term_msg'] = msg

        return render(request, self.template_name, self.data)

    #
    #
    #
    def post(self, request, *args, **kwargs):
        try:
            creditnote = CreditNode.objects.get(pk = int(kwargs["ins"]))
            creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
            
        except:
            return redirect('/unauthorized/', permanent=False)

        if request.method == 'POST':
            name = request.POST.get("customerName")
            email = request.POST.get("Email_Address")
            cc_email = request.POST.get("CC_Email_Address")
            address = request.POST.get("BillingAddress")
            creditnote_date = request.POST.get("CreditNoteDate")
            supply = request.POST.get("supplyPlace")
            invoice_reference = request.POST.get("Reference",'None')
            credit_number = request.POST.get("CreditNoteNumber",'None')
            creditnote_number = request.POST.get("creditnote_number_default",'off')
            term_condition = request.POST.get("t&c")
            message = request.POST.get("Message")
            attachement = request.POST.get("Attachment")
            subtotal = request.POST.get("SubTotal")
            cgst_5 = request.POST.get("CGST_5")
            sgst_5 = request.POST.get("SGST_5")
            igst_5 = request.POST.get("IGST_5")
            cgst_12 = request.POST.get("CGST_12")
            sgst_12 = request.POST.get("SGST_12")
            igst_12 = request.POST.get("IGST_12")
            cgst_18 = request.POST.get("CGST_18")
            sgst_18 = request.POST.get("SGST_18")
            igst_18 = request.POST.get("IGST_18")
            cgst_28 = request.POST.get("CGST_28")
            sgst_28 = request.POST.get("SGST_28")
            igst_28 = request.POST.get("IGST_28")
            cgst_other = request.POST.get("CGST_other")
            sgst_other = request.POST.get("SGST_other")
            igst_other = request.POST.get("IGST_other")
            total = request.POST.get("Total","None")
            default = request.POST.get('default','off')
            if(default == 'on'):
                # org = Organisations.objects.filter(user = request.user)
                # if(len(org) == 0):
                #     org2 = Organisations(user = request.user, terms_and_condition = term_condition)
                #     org2.save()
                # else:
                #     org.terms_and_condition = term_condition
                #     org.save()
                org = Organisations.objects.get(user = request.user)
                if(org.terms_and_condition is None):
                    org.terms_and_condition = term_condition
                    org.save()
                    # org2 = Organisations(user = request.user, terms_and_condition = term_condition)
                    # org2.save()
                elif(org.terms_and_condition is not None):
                    Organisations.objects.get(user = request.user).update(terms_and_condition = term_condition)

            if 'save_send' in request.POST:
                save_type = 1
            elif 'save_close' in request.POST:
                save_type = 2
            elif 'save_draft' in request.POST:
                save_type = 3
            
            contact = Contacts.objects.get(Q(user = request.user) & Q(pk = int(name)))
            CreditNode.objects.filter(pk = int(kwargs["ins"])).update(contact_name = contact,save_type = save_type,email=email,cc_email=cc_email,billing_address=address,
                                credit_date=creditnote_date,state_supply= supply,invoice_refrence=invoice_reference,credit_number=credit_number,
                                creditnote_number_check=creditnote_number,terms_and_condition=term_condition,Note=message,attachements=attachement,
                                sub_total=subtotal,cgst_5 = cgst_5 ,igst_5 = igst_5,sgst_5 = sgst_5,cgst_12 = cgst_12,igst_12 = igst_12,
                                sgst_12 = sgst_12,cgst_18 = cgst_18,igst_18 = igst_18,sgst_18 = sgst_18,cgst_28 = cgst_28,igst_28 = igst_28,
                                sgst_28 = sgst_28,cgst_other=cgst_other,igst_other = igst_other,sgst_other = sgst_other,total=total)

            product_name = request.POST.getlist('ItemName[]',None)
            product_desc = request.POST.getlist('desc[]',None)
            product_type = request.POST.getlist('type[]',None)
            # product_currency = request.POST.getlist('currency[]',None)
            product_price = request.POST.getlist('Price[]',None)
            product_unit = request.POST.getlist('Unit[]',None)
            product_quantity = request.POST.getlist('Quantity[]',None)
            product_discount = request.POST.getlist('Discount[]',None)
            product_discount_type = request.POST.getlist('Dis[]',None)
            product_tax = request.POST.getlist('tax[]',None)
            product_amount = request.POST.getlist('Amount[]',None)

            creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote)).delete()

            count = len(product_name)
            for i in range(0,count):

                if(product_name[i] == '-------' ):
                    products = None
                    if(len(product_desc[i]) > 0 or len(product_amount[i]) > 0):
                        CreditNode.objects.filter(pk = int(kwargs["ins"])).update(amount = product_amount[i], description = product_desc[i])
                    # credit.amount = product_amount[i]
                    # credit.description = product_desc[i]
                    # credit.save()
                    
                else:
                    products = ProductsModel.objects.get(pk = int(product_name[i]))
                    creditnote_item = creditnote_Items(user= request.user,credit_inventory= creditnote,product=products,description=product_desc[i],
                                                product_type=product_type[i],price=product_price[i],unit=product_unit[i],
                                                quantity=product_quantity[i],discount_type = product_discount_type[i],discount=product_discount[i],
                                                tax=product_tax[i],amount=product_amount[i])
                    creditnote_item.save()   

            #
            # PDF CODE
            #

            #
            # EMAIL SENDING FUNCTION
            #

            attach_check = request.POST.get("attach_check", False)
            
            if(save_type == 1):        
                if attach_check:
                    credit_note_mailer(request, creditnote, contact, send_attachments = True)
                else:
                    credit_note_mailer(request, creditnote, contact, send_attachments = False)
            
        return redirect('/creditnotes/', permanent = False)

#=====================================================================================
#   CLONE CREDITNOTE 
#=====================================================================================
#
class CloneCreditnote(View):

    # Template 
    template_name = 'app/app_files/creditnote/clone_creditnote.html'

    # Initialize 
    data = defaultdict()
    data["view"] = ""

    # Custom CSS/JS Files For Inclusion into template
    data["css_files"] = []
    data["js_files"] = ['custom_files/js/creditnote.js','custom_files/js/product.js','custom_files/js/contacts.js']
    data["active_link"] = 'Credit Note'
    data["breadcrumb_title"] = 'CREDIT NOTE' 

    # data["included_template"] = 'app/app_files/creditnote/clone_creditnote.html'

    # Initialize Forms
    data["contact_form"] = ContactsForm()
    data["tax_form"] = TaxForm()
    data["other_details_form"] = OtherDetailsForm()
    data["social_form"] = ContactsExtraForm()

    # FORMSETS    
    data["address_formset"] = AddressFormset
    data["accounts_formset"] = AccountsFormset

    def get(self, request, *args, **kwargs):
            
        try:
            creditnote = CreditNode.objects.get(pk = int(kwargs["ins"]))
            contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))
            products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
            creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
            default = Organisations.objects.filter(user = request.user)
        except:
            return redirect('/unauthorized/', permanent=False)

        # check we make a copy or note 
        strg1 = str(creditnote.contact_name)
        strg2 = strg1.split(' -')
        contact_result = contacts.filter(contact_name__iexact = strg2[0]).exists()
        if(contact_result != True):
            self.data['creditnote_contact_status2'] = 'NO'
        elif(contact_result == True):
            self.data['creditnote_contact_status2'] = 'YES'

        a = []
        for i in range(0,len(creditnote_item)):
            strg3 = str(creditnote_item[i].product)
            strg4 = strg3.split(' -')
            result = products.filter(product_name__iexact = strg4[0]).exists()
            if(result == True):
                a.append(creditnote_item[i])

        if(len(creditnote_item) != len(a)):
            self.data['creditnote_product_status2'] = 'NO'
        else:
            self.data['creditnote_product_status2'] = 'YES'
        
        self.data["contacts"] = contacts
        self.data["state"] = creditnote_constant.state
        self.data['tax'] = creditnote_constant.tax
        self.data["products"] = products
        self.data["credit_note"] = creditnote
        # if(len(a) > 0):
        self.data["creditnote_item"] = a

        self.data["item_count"] = len(creditnote_item)-1

        # Product form
        self.data["add_product_images_form"] = ProductPhotosForm()
        self.data["add_product_form"] = ProductForm(request.user)
        if( len(default) > 0):
            msg = default[0].terms_and_condition
            self.data['term_msg'] = msg



        return render(request, self.template_name, self.data)


#=====================================================================================
#   CLONE CREDITNOTE 
#=====================================================================================
#
def state_compare(request):
    user_organization = Organisations.objects.filter(user = request.user)
    
    if(len(user_organization) == 0):
        state = 'none'
    elif(user_organization[0].state is None):
        state = 'none'
    else:
        state = user_organization[0].get_state_display()
    data = {'state': state}
    return JsonResponse(data)
    
#=====================================================================================
#   PRINT CREDITNOTE 
#=====================================================================================
#
def print_credit_note(request, ins):

    template_name = 'app/app_files/creditnote/print_creditnote.html'
    # Initialize 
    data = defaultdict()
    try:
        creditnote = CreditNode.objects.get(pk = int(ins))
        organisation = Organisations.objects.get(user = request.user)
        organisation_contact = Organisation_Contact.objects.filter(organisation = organisation)
        
        
        # contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True))
        # products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True))
        creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
        
        # default = Organisations.objects.filter(user = request.user)
            
    except:
        return redirect('/unauthorized/', permanent=False)

    strg1 = str(creditnote.contact_name)
    word = strg1.find(' - ') 

    if(int(word) == int(-1)):
        data["contact_name"] = strg1
    elif(int(word) != int(-1)):
        strg2 = strg1.split(' - ')
        strg3 = strg2[1]
        count = len(strg3)
        data["contact_name"] = strg3[1:(count)-1]
        
    data["credit_note"] = creditnote
    data["creditnote_item"] = creditnote_item
    data['organisation'] = organisation
    data['organisation_contact'] = organisation_contact
    
    data['state'] = organisation.get_state_display()
    data['country'] = organisation.get_country_display()
    
    return render(request,template_name,data)
   
#   
#****************************************************************************************
# Code By : Lawrence Gandhar
# Common mailer function for sending credit note mail_send
# pass request, creditnote and contact instances as arguments
#****************************************************************************************

def credit_note_mailer(request, creditnote = None, contact = None, send_attachments = True):

    if creditnote is not None and contact is not None: 

        if creditnote.email !="":
    
            organisation = None

            try:
                organisation = Organisations.objects.get(user = request.user)
                subject = "Credit Note - {} from {} to {}".format(creditnote.credit_number, organisation.organisation_name, contact.contact_name)
            except:
                subject = "Credit Note - {} to {}".format(creditnote.credit_number,contact.contact_name)
        
            msg_body = ["Dear {},".format(creditnote.credit_number,contact.contact_name)]
            msg_body.append("Please find attached the Credit Note {} for your reference.".format(creditnote.credit_number))
            msg_body.append("<div style='padding:10px; border:1px solid #000000'>")
            msg_body.append("Credit Note - {}".format(creditnote.credit_number))
            msg_body.append("Credit Note Date - {}".format(datetime.now()))
            msg_body.append("Amount - {}".format(creditnote.total)) 
            msg_body.append("</div>")
            msg_body.append("Please feel free to contact us if you have any questions.")
            msg_body.append("Regards,")

            if organisation is not None:
                msg_body.append(organisation.organisation_name)

            msg_body = '<br>'.join(msg_body)

            msg_html = "<html><body>"+msg_body+"</body></html>"

            to_list = [email_id for email_id in creditnote.email.split(",")]
            cc_list = [cc_email_id for cc_email_id in creditnote.cc_email.split(",")]
        
            attachements = []
            if str(creditnote.attachements) !="" and send_attachments:
                attachements = [os.path.join(settings.MEDIA_ROOT,str(creditnote.attachements))]   
        
            msg = email_helper.Email_Helper(to=to_list, cc=cc_list, subject=subject, message=msg_html, attachment=attachements)
            msg.mail_send()
            
            #
            
            return True
        return False
    return False
    
#
#
#

def send_creditnote(request, ins=None):
    if request.is_ajax():
            
        try:
            creditnote = CreditNode.objects.get(pk = int(ins))
        except:
            return HttpResponse(0)
            
        try:
            contact = Contacts.objects.get(pk = creditnote.contact_name_id, user = request.user)
        except:
            return HttpResponse(0)   
            
            
         
        if credit_note_mailer(request, creditnote, contact, send_attachments = True):
            return HttpResponse(1) 
        return HttpResponse(0) 
    return HttpResponse(0) 