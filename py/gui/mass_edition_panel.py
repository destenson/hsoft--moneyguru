# Created By: Virgil Dupras
# Created On: 2008-07-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from hsutil.currency import Currency
from hsutil.misc import allsame, nonone, flatten

from ..exception import OperationAborted
from .base import GUIPanel
from .complete import TransactionCompletionMixIn

class MassEditionPanel(GUIPanel, TransactionCompletionMixIn):
    def __init__(self, view, document):
        GUIPanel.__init__(self, view, document)
        self._init_fields()
    
    #--- Override
    def _load(self):
        transactions = self.document.selected_transactions
        if len(transactions) < 2:
            raise OperationAborted()
        self._init_fields()
        self.can_change_accounts_and_amount = all(len(t.splits) == 2 for t in transactions)
        first = transactions[0]
        if allsame(t.date for t in transactions):
            self._date = first.date
        if allsame(t.description for t in transactions):
            self._description = first.description
        if allsame(t.payee for t in transactions):
            self._payee = first.payee
        if allsame(t.checkno for t in transactions):
            self._checkno = first.checkno
        splits = flatten(t.splits for t in transactions)
        splits = [s for s in splits if s.amount]
        if splits and allsame(s.amount.currency for s in splits):
            self._currency_index = Currency.all.index(splits[0].amount.currency)
        if not self.can_change_accounts_and_amount:
            return
        def get_from(t):
            s1, s2 = t.splits
            return s1 if s1.amount <=0 else s2
        
        def get_to(t):
            s1, s2 = t.splits
            return s2 if s1.amount <=0 else s1
        
        def get_name(split):
            return split.account.name if split.account is not None else ''
        
        if allsame(get_name(get_from(t)) for t in transactions):
            self._from = get_name(get_from(first))
        if allsame(get_name(get_to(t)) for t in transactions):
            self._to = get_name(get_to(first))
        if allsame(abs(t.splits[0].amount) for t in transactions):
            self._amount = abs(first.splits[0].amount)
    
    def _save(self):
        transactions = self.document.selected_transactions
        kw = {}
        if self.date_enabled:
            kw['date'] = self._date
        if self.description_enabled:
            kw['description'] = self._description
        if self.payee_enabled:
            kw['payee'] = self._payee
        if self.checkno_enabled:
            kw['checkno'] = self._checkno
        if self.from_enabled:
            kw['from_'] = self._from
        if self.to_enabled:
            kw['to'] = self._to
        if self.amount_enabled:
            kw['amount'] = self._amount
        if self.currency_enabled:
            kw['currency'] = Currency.all[self._currency_index]
        self.document.change_transactions(transactions, **kw)
    
    #--- Private
    def _init_fields(self):
        self.can_change_accounts_and_amount = False
        self.date_enabled = False
        self.description_enabled = False
        self.payee_enabled = False
        self.checkno_enabled = False
        self.from_enabled = False
        self.to_enabled = False
        self.amount_enabled = False
        self.currency_enabled = False
        self._date = date.today()
        self._description = ''
        self._payee = ''
        self._checkno = ''
        self._from = ''
        self._to = ''
        self._amount = 0
        self._currency_index = -1
    
    #--- Properties
    @property
    def date(self):
        return self.app.format_date(self._date)
    
    @date.setter
    def date(self, value):
        date = self.app.parse_date(value)
        if date == self._date:
            return
        self._date = date
        self.date_enabled = True
        self.view.refresh()
    
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        description = nonone(value, '')
        if description == self._description:
            return
        self._description = description
        self.description_enabled = True
        self.view.refresh()
    
    @property
    def payee(self):
        return self._payee
    
    @payee.setter
    def payee(self, value):
        payee = nonone(value, '')
        if payee == self._payee:
            return
        self._payee = payee
        self.payee_enabled = True
        self.view.refresh()
    
    @property
    def checkno(self):
        return self._checkno
    
    @checkno.setter
    def checkno(self, value):
        checkno = nonone(value, '')
        if checkno == self._checkno:
            return
        self._checkno = checkno
        self.checkno_enabled = True
        self.view.refresh()
    
    @property
    def from_(self):
        return self._from
    
    @from_.setter
    def from_(self, value):
        from_ = nonone(value, '')
        if from_ == self._from:
            return
        self._from = from_
        self.from_enabled = True
        self.view.refresh()
    
    @property
    def to(self):
        return self._to
    
    @to.setter
    def to(self, value):
        to = nonone(value, '')
        if to == self._to:
            return
        self._to = to
        self.to_enabled = True
        self.view.refresh()
    
    @property
    def amount(self):
        return self.app.format_amount(self._amount)
    
    @amount.setter
    def amount(self, value):
        amount = self.app.parse_amount(value)
        if amount == self._amount:
            return
        self._amount = amount
        self.amount_enabled = True
        self.view.refresh()
    
    @property
    def currency_index(self):
        return self._currency_index
    
    @currency_index.setter
    def currency_index(self, value):
        if value == self._currency_index:
            return
        self._currency_index = value
        self.currency_enabled = value >= 0
        self.view.refresh()
    