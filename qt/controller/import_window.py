# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget

from moneyguru.gui.import_window import ImportWindow as ImportWindowModel, DAY, MONTH, YEAR
from .import_table import ImportTable
from ui.import_window_ui import Ui_ImportWindow

class ImportWindow(QWidget, Ui_ImportWindow):
    def __init__(self, doc):
        QWidget.__init__(self, None)
        self._setupUi()
        self.doc = doc
        self.model = ImportWindowModel(view=self, document=doc.model)
        self.table = ImportTable(dataSource=self.model, view=self.tableView)
        self.table.model.connect()
        self._setupColumns() # Can only be done after the model has been connected
        
        self.tabView.tabCloseRequested.connect(self.tabCloseRequested)
        self.tabView.currentChanged.connect(self.currentTabChanged)
        self.targetAccountComboBox.currentIndexChanged.connect(self.targetAccountChanged)
        self.importButton.clicked.connect(self.importClicked)
        self.swapButton.clicked.connect(self.swapClicked)
    
    def _setupUi(self):
        self.setupUi(self)
        self.tabView.setTabsClosable(True)
        self.tabView.setDrawBase(False)
        self.tabView.setDocumentMode(True)
        self.tabView.setUsesScrollButtons(True)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setHighlightSections(False)
        h.resizeSection(0, 28)
        
        # Can't set widget alignment in a layout in the Designer
        l = self.targetAccountLayout
        l.setAlignment(self.targetAccountLabel, Qt.AlignTop)
        l.setAlignment(self.targetAccountComboBox, Qt.AlignTop)
    
    #--- Event Handlers
    def currentTabChanged(self, index):
        self.model.selected_pane_index = index
    
    def importClicked(self):
        self.model.import_selected_pane()
    
    def swapClicked(self):
        swapType = self.swapOptionsComboBox.currentIndex()
        applyToAll = self.applyToAllCheckBox.isChecked()
        if swapType in (0, 1, 2):
            first, second = [(DAY, MONTH), (MONTH, YEAR), (DAY, YEAR)][swapType]
            if self.model.can_switch_date_fields(first, second):
                self.model.switch_date_fields(first, second, applyToAll)
        else:
            self.model.switch_description_payee(applyToAll)
    
    def tabCloseRequested(self, index):
        self.model.close_pane(index)
        self.tabView.removeTab(index)
    
    def targetAccountChanged(self, index):
        self.model.selected_target_account_index = index
    
    #--- model --> view
    def close(self):
        self.hide()
    
    def close_selected_tab(self):
        self.tabView.removeTab(self.tabView.currentIndex())
    
    def refresh(self):
        # We disconnect the combobox because we don't want the clear() call to set the selected 
        # target index in the model.
        self.targetAccountComboBox.currentIndexChanged.disconnect(self.targetAccountChanged)
        self.targetAccountComboBox.clear()
        self.targetAccountComboBox.addItems(self.model.target_account_names)
        self.targetAccountComboBox.currentIndexChanged.connect(self.targetAccountChanged)
        while self.tabView.count():
            self.tabView.removeTab(0)
        for pane in self.model.panes:
            self.tabView.addTab(pane.name)
    
    def update_selected_pane(self):
        index = self.model.selected_pane_index
        if index != self.tabView.currentIndex(): # this prevents infinite loops
            self.tabView.setCurrentIndex(index)
        self.targetAccountComboBox.setCurrentIndex(self.model.selected_target_account_index)
    