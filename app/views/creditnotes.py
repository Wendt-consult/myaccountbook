from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from django.views import View
from collections import OrderedDict, defaultdict
from django.contrib import messages

from app.models.contacts_model import Contacts
from app.models.users_model import *
from app.models.products_model import *
from app.models.creditnote_model import *
from app.models.customize_model import *
from app.models.accounts_model import *

from app.forms.products_form import * 
from app.forms.contact_forms import * 
from app.forms.tax_form import *
from app.forms.inc_fomsets import *
from app.forms.accounts_ledger_forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import string

from app.other_constants import creditnote_constant

from django.db.models import Q

import json, os, csv

from app.helpers import email_helper

from datetime import datetime

from django.conf import settings
import datetime
from datetime import datetime
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
    data['type'] = 'view'

    # Custom CSS/JS Files For Inclusion into template
    data["css_files"] = []
    data["js_files"] = ['custom_files/js/customize_view.js']

    data["included_template"] = 'app/app_files/creditnote/view_creditnote.html'
    
    #
    #
    def get(self, request):        

        credit_note = CreditNode.objects.filter(user = request.user, creditnote_delete_status = 0)
        self.data["credit_note"] = credit_note

        # logic for view journal entry view and query
        default_list = []
        credit_note = credit_note.exclude(save_type = 3)
        credit_note = credit_note.exclude(is_blank_credit = 'on')
        credit_count = len(credit_note)
        for i in range(0,credit_count):
            credit_item = creditnote_Items.objects.filter(credit_inventory = credit_note[i])
            item_count = len(credit_item)
            # revser_track = 0
            check_list = []
            for j in range(0,item_count):
                if credit_item[j].account.group_name not in check_list :
                    check_list.append(credit_item[j].account.group_name)
                    acc = credit_item.filter(account = credit_item[j].account)
                    acc_count = len(acc)
                    default_dic = {}
                    default_dic['ids'] = credit_note[i].id
                    default_dic['account_name'] = credit_item[j].account.group_name
                    calculate = 0.00
                    for k in range(0,acc_count):
                        calculate += float(acc[k].amount)
                    default_dic['value'] = '%.2f' % calculate
                    default_list.append(default_dic)
                    # default_dic.clear()

        self.data['default_list'] = default_list

        # CUSTOMIZE VIEW CODE
        customize_credit = CustomizeModuleName.objects.filter(Q(user = request.user) & Q(customize_name = 3))
        if(len(customize_credit) != 0):
            view_credit = CustomizeCreditView.objects.get(customize_view_name = customize_credit[0].id)
            if(view_credit is not None):
                self.data['customize'] = view_credit
            else:
                self.data['customize'] = 'NA'
        else:
                self.data['customize'] = 'NA'

        return render(request, self.template_name, self.data)

#=====================================================================================
#   ADD CREDITNOTE
#=====================================================================================
#
def add_creditnote(request, ins, slug ):

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
    data['type'] = 'add'
    
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

    # ACCOUNT_LEDGER FORMS
    data["groups_form"] = AccGroupsForm()

    # constant
    data['gst_code'] = country_list.GST_STATE_CODE
    # list contact name
    contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))
    
    default = Organisations.objects.filter(user = request.user)
    if(len(default) > 0):
        msg = default[0].terms_and_condition
        notes = default[0].note
        data['term_msg'] = msg
        data['notes'] = notes
    data["contacts"] = contacts
    data["state"] = country_list.STATE_LIST_CHOICES
    data['gst_r_type'] = user_constants.org_GST_REG_TYPE
    # data['tax'] = creditnote_constant.tax

    # gst tax model
    gst = users_model.OrganisationGSTSettings.objects.filter(user = request.user)
    data['gst'] = gst 
    # list product name
    if( int(ins) == 1):
        products = ProductsModel.objects.filter(user = request.user, is_active = True, product_delete_status = 0)
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
        # 
        # for account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Income')
        acc_ledger_income = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        acc_group_name = []
        acc_ids =[]
        acc_count = len(acc_ledger_income)
        for i in range(0,acc_count):
            acc_group_name.append(acc_ledger_income[i].group_name)
            acc_ids.append(acc_ledger_income[i].id)

        # for tax option
        tax = []
        org_gst = len(gst)
        for i in range(0,org_gst):
            tax.append(gst[i].taxname_percent)

        # common dictionary
        data = {'products': name, 'ids': ids, 'acc_group_name':acc_group_name,'acc_ids':acc_ids, 'gst':tax} 
        return JsonResponse(data)
    elif(int(ins) == 0):
        products = ProductsModel.objects.filter(user = request.user, is_active = True, product_delete_status = 0)
        data["products"] = products

        # for account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Income')
        acc_ledger_income = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        data['acc_ledger_income'] = acc_ledger_income

        # for purchase account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Expense')
        acc_ledger_expense = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        data['acc_ledger_expense'] = acc_ledger_expense

        # for coming to direct contact module
        data['direct_con'] = 'NA'
        if(slug != 'NA'):
            contacts = contacts.get(pk = int(slug))
            data['direct_con'] = contacts.id
            
        # org gst number
        data['is_gst'] = 'no'
        data['is_signle_gst']  = 'no'
        data['org_gst_type'] = None
        org = Organisations.objects.get(user = request.user)

        org_gst_num = User_Tax_Details.objects.filter(organisation = org.id,is_active = True)

        data['org_id'] = org.id
        if(len(org_gst_num) == 1):
            data['is_signle_gst'] = 'yes'
            data['is_gst'] = org_gst_num[0].gstin
            data['org_gst_type'] = org_gst_num[0].gst_reg_type
        elif(len(org_gst_num) > 0):
            default = org_gst_num.filter(default_gstin = True,is_active = True)
            if(len(default) != 0):
                data['is_gst'] = default[0].gstin
                data['org_gst_type'] = default[0].gst_reg_type
            else:
                data['is_gst'] = org_gst_num[0].gstin
                data['org_gst_type'] = org_gst_num[0].gst_reg_type

        

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
    address = User_Address_Details.objects.filter(Q(contact = slug) & Q(is_billing_address = 1) & Q(default_address = True)).values('contact_person','flat_no', 'street', 'city', 'state', 'country', 'pincode')
    if(len(address) != 0):
        for i in range(0,1):
            add=""
            for j in address[i].values():
                if( j is not None):
                    add+=str(j)+', '
            data['address'].append(add[0:(len(add))-2])
    else:
        address_new = User_Address_Details.objects.filter(Q(contact = slug) & Q(is_billing_address = 1)).values('contact_person','flat_no', 'street', 'city', 'state', 'country', 'pincode')
        if(len(address_new) != 0):
            for i in range(0,1):
                add_new=""
                for j in address_new[i].values():
                    if( j is not None):
                        add_new+=str(j)+', '
                data['address'].append(add_new[0:(len(add_new))-2])
    return JsonResponse(data)

#=====================================================================================
#   FETCH PRODUCT_type/Units/Price/Product Description/Currency
#=====================================================================================
#
def fetch_product(request, slug):
    
    # Initialize 
    data = defaultdict()
    products = ProductsModel.objects.get(pk = int(slug))
    data['is_check_selling'] = 'no'
    data['product'] = products.product_type
    data['unit'] = products.get_unit_display()
    data['price'] =  products.selling_price
    data['desc'] = products.product_description
    data['selling_tax'] = products.selling_tax
    if(products.inclusive_tax is not None):
        data['is_check_selling'] = 'yes'
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
            data['credit_number'] = 'CN-0001'
        else:
            inc = count+1
            for i in range(0,count):
                a = 'CN-000'+str(inc)
                result = credit_note.filter(Q(user = request.user) & Q(credit_number__iexact = a)).exists() 
                if(result == True):
                    inc += 1
                elif(result == False):
                    data['credit_number'] = 'CN-000'+str(inc)
                    break
        
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
        # change credit note date formate
        creditnote_date = datetime.strptime(str(creditnote_date), '%d-%m-%Y').strftime('%Y-%m-%d')
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
        # cgst_5 = request.POST.get("CGST_5")
        # sgst_5 = request.POST.get("SGST_5")
        # igst_5 = request.POST.get("IGST_5")
        # cgst_12 = request.POST.get("CGST_12")
        # sgst_12 = request.POST.get("SGST_12")
        # igst_12 = request.POST.get("IGST_12")
        # cgst_18 = request.POST.get("CGST_18")
        # sgst_18 = request.POST.get("SGST_18")
        # igst_18 = request.POST.get("IGST_18")
        # cgst_28 = request.POST.get("CGST_28")
        # sgst_28 = request.POST.get("SGST_28")
        # igst_28 = request.POST.get("IGST_28")
        # cgst_other = request.POST.get("CGST_other")
        # sgst_other = request.POST.get("SGST_other")
        # igst_other = request.POST.get("IGST_other")
        cgst = request.POST.get("CGST")
        sgst = request.POST.get("SGST")
        igst = request.POST.get("IGST")
        total = request.POST.get("Total","None")
        default = request.POST.get('default','off')
        creditnote_default_notes = request.POST.get('creditnote_default_notes','off')
        # for credit note gst number and type
        org_gst_number = request.POST.get("org_gst_number")
        org_gst_reg_type = request.POST.get("org_gst_reg_type")
        single_gst_code = request.POST.get("single_gst_code")
        is_blank_credit = request.POST.get("blank_credit_toggle",'off')
        if(default == 'on'):
            org = Organisations.objects.get(user = request.user)
            if(org.terms_and_condition is None):
                org.terms_and_condition = term_condition
                org.save()
            elif(org.terms_and_condition is not None):
                Organisations.objects.get(user = request.user).update(terms_and_condition = term_condition)

        if(creditnote_default_notes == 'on'):
            org = Organisations.objects.get(user = request.user)
            if(org.note is None):
                org.note = message
                org.save()
            elif(org.note is not None):
                Organisations.objects.get(user = request.user).update(note = message)
                

        if 'save_send' in request.POST:
            save_type = 1
        elif 'save_close' in request.POST:
            save_type = 2
        elif 'save_draft' in request.POST:
            save_type = 3

        contact = Contacts.objects.get(user = request.user, pk = int(name))

        
        credit = CreditNode(
            user= request.user, 
            contact_name = contact,
            save_type = save_type,
            email=email,
            cc_email=cc_email,
            billing_address=address,
            credit_date=creditnote_date,
            state_supply= supply,
            invoice_refrence=invoice_reference,
            credit_number=credit_number,
            creditnote_number_check=creditnote_number,
            terms_and_condition=term_condition,
            Note=message,
            attachements=attachement,
            sub_total=subtotal,
            cgst = cgst,
            sgst = sgst,
            igst = igst,
            total=total,
            creditnote_org_gst_num = org_gst_number,
            creditnote_org_gst_type = org_gst_reg_type,
            creditnote_org_gst_state = single_gst_code,
            is_blank_credit = is_blank_credit,
        )
        if(cgst != '' or sgst != ''):
            credit.is_cs_gst = True
        elif(igst != ''):
            credit.is_cs_gst = False

        credit.save()     
        
        
        # igst = list(filter(None, [igst_5, igst_12, igst_18, igst_28, igst_other]))
        # cgst = list(filter(None, [cgst_5, cgst_12, cgst_18, cgst_28,cgst_other]))
        # sgst = list(filter(None, [sgst_5, sgst_12, sgst_18, sgst_28, sgst_other]))
        # print(igst, cgst, sgst)
        
        if(is_blank_credit == 'on'):
            blank_desc = request.POST.get("blank_desc")
            blank_amount = request.POST.get("blank_amount")
            creditnote_item = creditnote_Items(
                user = request.user,
                credit_inventory = credit,
                description = blank_desc,
                amount = blank_amount,
            )
            creditnote_item.save() 
        else:
            product_name = request.POST.getlist('ItemName[]',None)
            product_desc = request.POST.getlist('desc[]',None)
            account_ids = request.POST.getlist('product_account[]',None)
            # product_type = request.POST.getlist('type[]',None)
            # product_currency = request.POST.getlist('currency[]',None)
            product_price = request.POST.getlist('Price[]',None)
            product_unit = request.POST.getlist('Unit[]',None)
            product_quantity = request.POST.getlist('Quantity[]',None)
            product_discount = request.POST.getlist('Discount[]',None)
            product_discount_type = request.POST.getlist('Dis[]',None)
            product_tax = request.POST.getlist('tax[]',None)
            product_cgst = request.POST.getlist('row_cgst[]',None)
            product_sgst = request.POST.getlist('row_sgst[]',None)
            product_igst = request.POST.getlist('row_igst[]',None)
            product_amount = request.POST.getlist('Amount[]',None)
            product_amount_inc = request.POST.getlist('Amount_inc[]',None)

            count = len(product_name)
            for i in range(0,count):
                if(product_name[i] != '-------' ):
                #     products = None
                #     if(len(product_desc[i]) > 0 or len(product_amount[i]) > 0):
                #         credit.amount = product_amount[i]
                #         credit.description = product_desc[i]
                #         credit.save()
                # else:
                    
                    products = ProductsModel.objects.get(pk = int(product_name[i]))
                    account = accounts_model.AccGroups.objects.get(pk = int(account_ids[i]))
                    creditnote_item = creditnote_Items(
                        user = request.user,
                        credit_inventory = credit,
                        product = products,
                        description = product_desc[i],
                        account=account,
                        # product_type = product_type[i],
                        price = product_price[i],
                        unit = product_unit[i],
                        quantity = product_quantity[i],
                        discount_type = product_discount_type[i],
                        discount = product_discount[i],
                        tax = product_tax[i],
                        cgst_amount = product_cgst[i],
                        sgst_amount = product_sgst[i],
                        igst_amount = product_igst[i],
                        amount = product_amount[i],
                        amount_inc = product_amount_inc[i],
                    )
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
    data['type'] = 'edit'

    data["included_template"] = 'app/app_files/creditnote/edit_creditnote.html'

    # Initialize Forms
    data["contact_form"] = ContactsForm()
    data["tax_form"] = TaxForm()
    data["other_details_form"] = OtherDetailsForm()
    data["social_form"] = ContactsExtraForm()

    # FORMSETS    
    data["address_formset"] = AddressFormset
    data["accounts_formset"] = AccountsFormset

    # ACCOUNT_LEDGER FORMS
    data["groups_form"] = AccGroupsForm()

    # constant
    data['gst_code'] = country_list.GST_STATE_CODE

    def get(self, request, *args, **kwargs):

        try:
            creditnote = CreditNode.objects.get(pk = int(kwargs["ins"]))
            contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))
            products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
            # inactive and delete product or contact
            intcontacts = Contacts.objects.filter(Q(user = request.user))
            intproducts = ProductsModel.objects.filter(Q(user = request.user))
            creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
            default = Organisations.objects.filter(user = request.user)
            gst = users_model.OrganisationGSTSettings.objects.filter(user = request.user)
    
        except:
            return redirect('/unauthorized/', permanent=False)

        # for account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Income')
        acc_ledger_income = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        self.data['acc_ledger_income'] = acc_ledger_income

        # for purchase account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Expense')
        acc_ledger_expense = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        self.data['acc_ledger_expense'] = acc_ledger_expense

        self.data["contacts"] = contacts
        self.data["state"] = country_list.STATE_LIST_CHOICES
        self.data['gst_r_type'] = user_constants.org_GST_REG_TYPE
        # self.data['tax'] = creditnote_constant.tax
        self.data['gst'] = gst 

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
        if(len(default) > 0):
            msg = default[0].terms_and_condition
            notes = default[0].note
            self.data['term_msg'] = msg
            self.data['notes'] = notes

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
            # change credit note date formate
            creditnote_date = datetime.strptime(str(creditnote_date), '%d-%m-%Y').strftime('%Y-%m-%d')
            supply = request.POST.get("supplyPlace")
            invoice_reference = request.POST.get("Reference",'None')
            credit_number = request.POST.get("CreditNoteNumber",'None')
            creditnote_number = request.POST.get("creditnote_number_default",'off')
            term_condition = request.POST.get("t&c")
            message = request.POST.get("Message")
            attachement = request.POST.get("Attachment")
            subtotal = request.POST.get("SubTotal")
            # cgst_5 = request.POST.get("CGST_5")
            # sgst_5 = request.POST.get("SGST_5")
            # igst_5 = request.POST.get("IGST_5")
            # cgst_12 = request.POST.get("CGST_12")
            # sgst_12 = request.POST.get("SGST_12")
            # igst_12 = request.POST.get("IGST_12")
            # cgst_18 = request.POST.get("CGST_18")
            # sgst_18 = request.POST.get("SGST_18")
            # igst_18 = request.POST.get("IGST_18")
            # cgst_28 = request.POST.get("CGST_28")
            # sgst_28 = request.POST.get("SGST_28")
            # igst_28 = request.POST.get("IGST_28")
            # cgst_other = request.POST.get("CGST_other")
            # sgst_other = request.POST.get("SGST_other")
            # igst_other = request.POST.get("IGST_other")
            cgst = request.POST.get("CGST")
            sgst = request.POST.get("SGST")
            igst = request.POST.get("IGST")
            total = request.POST.get("Total","None")
            default = request.POST.get('default','off')
            creditnote_default_notes = request.POST.get('creditnote_default_notes','off')
            # for invoice gst number and type
            org_gst_number = request.POST.get("org_gst_number")
            org_gst_reg_type = request.POST.get("org_gst_reg_type")
            single_gst_code = request.POST.get("single_gst_code")
            is_blank_credit = request.POST.get("blank_credit_toggle",'off')
            if(default == 'on'):
                org = Organisations.objects.get(user = request.user)
                if(org.terms_and_condition is None):
                    org.terms_and_condition = term_condition
                    org.save()
                elif(org.terms_and_condition is not None):
                    Organisations.objects.get(user = request.user).update(terms_and_condition = term_condition)

            if(creditnote_default_notes == 'on'):
                org = Organisations.objects.get(user = request.user)
                if(org.note is None):
                    org.note = message
                    org.save()
                elif(org.note is not None):
                    Organisations.objects.get(user = request.user).update(note = message)

            if 'save_send' in request.POST:
                save_type = 1
            elif 'save_close' in request.POST:
                save_type = 2
            elif 'save_draft' in request.POST:
                save_type = 3
            
            contact = Contacts.objects.get(Q(user = request.user) & Q(pk = int(name)))
            CreditNode.objects.filter(pk = int(kwargs["ins"])).update(
                contact_name = contact,
                save_type = save_type,
                email=email,
                cc_email=cc_email,
                billing_address=address,
                credit_date=creditnote_date,
                state_supply= supply,
                invoice_refrence=invoice_reference,
                credit_number=credit_number,
                creditnote_number_check=creditnote_number,
                terms_and_condition=term_condition,
                Note=message,
                attachements=attachement,
                sub_total=subtotal,
                cgst = cgst,
                sgst = sgst,
                igst = igst,
                total=total,
                creditnote_org_gst_num = org_gst_number,
                creditnote_org_gst_type = org_gst_reg_type,
                creditnote_org_gst_state = single_gst_code,
                is_blank_credit = is_blank_credit,
                )
            if(cgst != '' or sgst != ''):
                CreditNode.objects.filter(pk = int(kwargs["ins"])).update(is_cs_gst = True)
            else:
                CreditNode.objects.filter(pk = int(kwargs["ins"])).update(is_cs_gst = False)


            creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote)).delete()

            if(is_blank_credit == 'on'):
                blank_desc = request.POST.get("blank_desc")
                blank_amount = request.POST.get("blank_amount")
                creditnote_item = creditnote_Items(
                    user = request.user,
                    credit_inventory = creditnote,
                    description = blank_desc,
                    amount = blank_amount,
                )
                creditnote_item.save()   
            else:
                product_name = request.POST.getlist('ItemName[]',None)
                product_desc = request.POST.getlist('desc[]',None)
                account_ids = request.POST.getlist('product_account[]',None)
                # product_type = request.POST.getlist('type[]',None)
                # product_currency = request.POST.getlist('currency[]',None)
                product_price = request.POST.getlist('Price[]',None)
                product_unit = request.POST.getlist('Unit[]',None)
                product_quantity = request.POST.getlist('Quantity[]',None)
                product_discount = request.POST.getlist('Discount[]',None)
                product_discount_type = request.POST.getlist('Dis[]',None)
                product_tax = request.POST.getlist('tax[]',None)
                product_cgst = request.POST.getlist('row_cgst[]',None)
                product_sgst = request.POST.getlist('row_sgst[]',None)
                product_igst = request.POST.getlist('row_igst[]',None)
                product_amount = request.POST.getlist('Amount[]',None)
                product_amount_inc = request.POST.getlist('Amount_inc[]',None)

                count = len(product_name)
                for i in range(0,count):

                    if(product_name[i] != '-------' ):
                        # products = None
                        # if(len(product_desc[i]) > 0 or len(product_amount[i]) > 0):
                            # CreditNode.objects.filter(pk = int(kwargs["ins"])).update(amount = product_amount[i], description = product_desc[i])
                        # credit.amount = product_amount[i]
                        # credit.description = product_desc[i]
                        # credit.save()   
                    # else:
                        products = ProductsModel.objects.get(pk = int(product_name[i]))
                        account = accounts_model.AccGroups.objects.get(pk = int(account_ids[i]))
                        creditnote_item = creditnote_Items(
                            user = request.user,
                            credit_inventory = creditnote,
                            product = products,
                            description = product_desc[i],
                            account=account,
                            # product_type = product_type[i],
                            price = product_price[i],
                            unit = product_unit[i],
                            quantity = product_quantity[i],
                            discount_type = product_discount_type[i],
                            discount = product_discount[i],
                            tax = product_tax[i],
                            cgst_amount = product_cgst[i],
                            sgst_amount = product_sgst[i],
                            igst_amount = product_igst[i],
                            amount = product_amount[i],
                            amount_inc = product_amount_inc[i],
                        )
                        creditnote_item.save()   


            #******************************************************************************
            #  Added By Lawrence : Execute On Credit Note Edit
            #******************************************************************************
            #
            # credit_note = CreditNode.objects.get(pk = int(kwargs["ins"]))

            # igst_amount = list(filter(None, [credit_note.igst_5, credit_note.igst_12, credit_note.igst_18, credit_note.igst_28, credit_note.igst_other]))
            # cgst_amount = list(filter(None, [credit_note.cgst_5, credit_note.cgst_12, credit_note.cgst_18, credit_note.cgst_28, credit_note.cgst_other]))
            # sgst_amount = list(filter(None, [credit_note.sgst_5, credit_note.sgst_12, credit_note.sgst_18, credit_note.sgst_28, credit_note.sgst_other]))
            
            # igst_amount = [ float(i) for i in igst_amount]
            # cgst_amount = [ float(i) for i in cgst_amount]
            # sgst_amount = [ float(i) for i in sgst_amount]


            # gst_ledger = gst_ledger_model.GST_Ledger.objects.get(creditnote=credit_note)

            # gst_ledger.gst_number = credit_note.creditnote_org_gst_num
            # gst_ledger.cgst_amount = sum(cgst_amount)
            # gst_ledger.sgst_amount = sum(sgst_amount)
            # gst_ledger.igst_amount = sum(igst_amount)
            # gst_ledger.is_creditnote = True
            # gst_ledger.total_tax = gst_ledger.cgst_amount + gst_ledger.sgst_amount + gst_ledger.igst_amount

            # gst_ledger.user = credit_note.user

            # gst_ledger.save()

            #******************************************************************************
            # Code End
            #******************************************************************************
            #

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
    data['type'] = 'clone'

    # data["included_template"] = 'app/app_files/creditnote/clone_creditnote.html'

    # Initialize Forms
    data["contact_form"] = ContactsForm()
    data["tax_form"] = TaxForm()
    data["other_details_form"] = OtherDetailsForm()
    data["social_form"] = ContactsExtraForm()

    # FORMSETS    
    data["address_formset"] = AddressFormset
    data["accounts_formset"] = AccountsFormset

    # constant
    data['gst_code'] = country_list.GST_STATE_CODE

    # ACCOUNT_LEDGER FORMS
    data["groups_form"] = AccGroupsForm()

    def get(self, request, *args, **kwargs):
            
        try:
            creditnote = CreditNode.objects.get(pk = int(kwargs["ins"]))
            contacts = Contacts.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(contact_delete_status = 0))
            products = ProductsModel.objects.filter(Q(user = request.user) & Q(is_active = True) & Q(product_delete_status = 0))
            # inactive and delete product or contact
            intcontacts = Contacts.objects.filter(Q(user = request.user))
            intproducts = ProductsModel.objects.filter(Q(user = request.user))

            creditnote_item = creditnote_Items.objects.filter(Q(user= request.user) & Q(credit_inventory = creditnote))
            default = Organisations.objects.filter(user = request.user)
            gst = users_model.OrganisationGSTSettings.objects.filter(user = request.user)
        except:
            return redirect('/unauthorized/', permanent=False)

        # for account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Income')
        acc_ledger_income = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        self.data['acc_ledger_income'] = acc_ledger_income

        # for purchase account_ledger details
        major_heads = accounts_model.MajorHeads.objects.get(major_head_name = 'Expense')
        acc_ledger_expense = accounts_model.AccGroups.objects.filter(Q(user = request.user) & Q(major_head = major_heads))
        self.data['acc_ledger_expense'] = acc_ledger_expense

        # check we make a copy or note 
        strg1 = str(creditnote.contact_name)
        strg2 = strg1.split(' -')
        contact_result = contacts.filter(contact_name__iexact = strg2[0]).exists()
        if(contact_result != True):
            self.data['creditnote_contact_status2'] = 'NO'
        elif(contact_result == True):
            self.data['creditnote_contact_status2'] = 'YES'

        if(creditnote.is_blank_credit == 'off'):
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
        else:
            self.data['creditnote_product_status2'] = 'YES'
        
        # inactive and delete product or contact
        self.data["intproducts"] = intproducts
        self.data["intcontacts"] = intcontacts
        self.data["contacts"] = contacts
        self.data["state"] = country_list.STATE_LIST_CHOICES
        # self.data['tax'] = creditnote_constant.tax
        self.data["products"] = products
        self.data["credit_note"] = creditnote
        self.data['gst'] = gst 
        # if(len(a) > 0):
        self.data["creditnote_item"] = creditnote_item

        self.data["item_count"] = len(creditnote_item)-1

        # Product form
        self.data["add_product_images_form"] = ProductPhotosForm()
        self.data["add_product_form"] = ProductForm(request.user)

        if(len(default) > 0):
            msg = default[0].terms_and_condition
            notes = default[0].note
            self.data['term_msg'] = msg
            self.data['notes'] = notes
        
        # org gst number
        self.data['is_gst'] = 'no'
        self.data['is_signle_gst']  = 'no'
        self.data['org_gst_type'] = None
        org = Organisations.objects.get(user = request.user)

        org_gst_num = User_Tax_Details.objects.filter(organisation = org.id,is_active = True)

        self.data['org_id'] = org.id
        if(len(org_gst_num) == 1):
            self.data['is_signle_gst'] = 'yes'
            self.data['is_gst'] = org_gst_num[0].gstin
            self.data['org_gst_type'] = org_gst_num[0].gst_reg_type
        elif(len(org_gst_num) > 0):
            default = org_gst_num.filter(default_gstin = True,is_active = True)
            if(len(default) != 0):
                self.data['is_gst'] = default[0].gstin
                self.data['org_gst_type'] = default[0].gst_reg_type
            else:
                self.data['is_gst'] = org_gst_num[0].gstin
                self.data['org_gst_type'] = org_gst_num[0].gst_reg_type

        return render(request, self.template_name, self.data)


#=====================================================================================
#   CLONE CREDITNOTE 
#=====================================================================================
#
def state_compare(request):
    # Initialize 
    data = defaultdict()
    data['gst'] = ''
    data['gst_type'] = ''
    org = users_model.Organisations.objects.get(user = request.user)
    org_address = users_model.User_Address_Details.objects.filter(Q(is_user = True) & Q(is_organisation = True) & Q(organisation = org) & Q(default_address = True))
    if(len(org_address) != 0):
        if(org_address[0].organisation_tax !=''):
            data['gst'] = org_address[0].organisation_tax.gstin
            data['gst_type'] = org_address[0].gst_reg_type
    else:
        first_address = users_model.User_Address_Details.objects.filter(Q(is_user = True) & Q(is_organisation = True) & Q(organisation = org))
        
        if(len(first_address) != 0):
            data['gst'] = first_address[0].organisation_tax.gstin
            data['gst_type'] = first_address[0].gst_reg_type
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
        address = users_model.User_Address_Details.objects.filter(Q(organisation = organisation) & Q(is_organisation = True) & Q(is_user = True) & Q(default_address = True))
        
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
    
    if(len(address) == 1):
        data['org_address'] = address[0]
        data['state'] = address[0].get_state_display()
        data['country'] = address[0].get_country_display()
    elif(len(address) == 0):
        org_address = users_model.User_Address_Details.objects.filter(Q(organisation = organisation))
        if(len(org_address) != 0):
            data['org_address'] = org_address[0]
            data['state'] = org_address[0].get_state_display()
            data['country'] = org_address[0].get_country_display()

    # data['state'] = organisation.get_state_display()
    # data['country'] = organisation.get_country_display()
    
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
        
            msg_body = ["Dear {},".format(contact.contact_name)]
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

#=====================================================================================
#   DELETE CREDIT_NOTE
#=====================================================================================
#

def delete_credit_note(request, ins):
    if ins is not None:
        try:
            CreditNode.objects.filter(pk = int(ins)).update(creditnote_delete_status = 1)
        
        except:
            return redirect('/unauthorized/', permanent=False)

        # Purchase_Items.objects.filter(Q(user= request.user) & Q(purchase_item_list = purchase_order)).delete()
        # PurchaseOrder.objects.get(pk = int(ins)).delete()

        return redirect('/creditnotes/', permanent=False)
    return redirect('/unauthorized/', permanent=False)