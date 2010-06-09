# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys

from PyQt4.QtCore import Qt, QProcess
from PyQt4.QtGui import QMainWindow, QPrintDialog, QMessageBox

from core.const import PaneType
from core.gui.main_window import MainWindow as MainWindowModel

from print_ import ViewPrinter
from support.recent import Recent
from support.search_edit import SearchEdit
from .account.view import EntryView
from .budget.view import BudgetView
from .networth.view import NetWorthView
from .profit.view import ProfitView
from .transaction.view import TransactionView
from .schedule.view import ScheduleView
from .new_view import NewView
from .lookup import AccountLookup, CompletionLookup
from .account_panel import AccountPanel
from .account_reassign_panel import AccountReassignPanel
from .transaction_panel import TransactionPanel
from .mass_edition_panel import MassEditionPanel
from .schedule_panel import SchedulePanel
from .budget_panel import BudgetPanel
from .custom_date_range_panel import CustomDateRangePanel
from .search_field import SearchField
from .date_range_selector import DateRangeSelector
from ui.main_window_ui import Ui_MainWindow

# IMPORTANT NOTE ABOUT TABS
# Why don't we use a QTabWidget? Because it doesn't allow to add the same widget twice.

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.app = doc.app
        
        self._setupUi()
        
        # Create base elements
        self.model = MainWindowModel(view=self, document=doc.model)
        self.nwview = NetWorthView(mainwindow=self)
        self.pview = ProfitView(mainwindow=self)
        self.tview = TransactionView(mainwindow=self)
        self.eview = EntryView(mainwindow=self)
        self.scview = ScheduleView(mainwindow=self)
        self.bview = BudgetView(mainwindow=self)
        self.newview = NewView(mainwindow=self)
        self.apanel = AccountPanel(mainwindow=self)
        self.tpanel = TransactionPanel(mainwindow=self)
        self.mepanel = MassEditionPanel(mainwindow=self)
        self.scpanel = SchedulePanel(mainwindow=self)
        self.bpanel = BudgetPanel(mainwindow=self)
        self.cdrpanel = CustomDateRangePanel(self, mainwindow=self)
        self.arpanel = AccountReassignPanel(self, mainwindow=self)
        self.alookup = AccountLookup(self, mainwindow=self)
        self.clookup = CompletionLookup(self, mainwindow=self)
        self.drsel = DateRangeSelector(mainwindow=self, view=self.dateRangeSelectorView)
        self.sfield = SearchField(mainwindow=self, view=self.searchLineEdit)
        self.recentDocuments = Recent(self.app, self.menuOpenRecent, 'recentDocuments')
        
        # Set main views
        self.mainView.addWidget(self.nwview)
        self.mainView.addWidget(self.pview)
        self.mainView.addWidget(self.tview)
        self.mainView.addWidget(self.eview)
        self.mainView.addWidget(self.scview)
        self.mainView.addWidget(self.bview)
        self.mainView.addWidget(self.newview)
        
        # set_children() and connect() calls have to happen after _setupUiPost()
        children = [self.nwview, self.pview, self.tview, self.eview, self.scview, self.bview,
            self.newview, self.apanel, self.tpanel, self.mepanel, self.scpanel, self.bpanel,
            self.cdrpanel, self.arpanel, self.alookup, self.clookup, self.drsel]
        self.model.set_children([child.model for child in children])
        self.model.connect()
        self.sfield.model.connect()
        
        self._updateUndoActions()
        self._bindSignals()
    
    def _setupUi(self): # has to take place *before* base elements creation
        self.setupUi(self)
        self.tabBar.setMovable(True)
        self.tabBar.setTabsClosable(True)
        
        # Toolbar setup. We have to do it manually because it's tricky to insert the view title
        # label otherwise.
        self.toolBar.addAction(self.actionShowNetWorth)
        self.toolBar.addAction(self.actionShowProfitLoss)
        self.toolBar.addAction(self.actionShowTransactions)
        self.toolBar.addAction(self.actionShowSchedules)
        self.toolBar.addAction(self.actionShowBudgets)
        self.toolBar.addSeparator()
        self.searchLineEdit = SearchEdit()
        self.searchLineEdit.setMaximumWidth(240)
        self.toolBar.addWidget(self.searchLineEdit)
        
        # Restore window size
        # We don't set geometry if the window was maximized so that if the user de-maximize the
        # window, it actually shrinks.
        if self.app.prefs.mainWindowRect is not None and not self.app.prefs.mainWindowIsMaximized:
            self.setGeometry(self.app.prefs.mainWindowRect)

        # Linux setup
        if sys.platform == 'linux2':
            self.actionCheckForUpdate.setVisible(False) # This only works on Windows
    
    def _bindSignals(self):
        self.recentDocuments.mustOpenItem.connect(self.doc.open)
        self.doc.documentOpened.connect(self.recentDocuments.insertItem)
        self.doc.documentSavedAs.connect(self.recentDocuments.insertItem)
        self.app.willSavePrefs.connect(self._savePrefs)
        self.tabBar.currentChanged.connect(self.currentTabChanged)
        self.tabBar.tabCloseRequested.connect(self.tabCloseRequested)
        self.tabBar.tabMoved.connect(self.tabMoved)
        
        # Views
        self.actionShowNetWorth.triggered.connect(self.showNetWorthTriggered)        
        self.actionShowProfitLoss.triggered.connect(self.showProfitLossTriggered)        
        self.actionShowTransactions.triggered.connect(self.showTransactionsTriggered)        
        self.actionShowSchedules.triggered.connect(self.showSchedulesTriggered)        
        self.actionShowBudgets.triggered.connect(self.showBudgetsTriggered)        
        self.actionShowPreviousView.triggered.connect(self.showPreviousViewTriggered)        
        self.actionShowNextView.triggered.connect(self.showNextViewTriggered)        
        
        # Document Edition
        self.actionNewItem.triggered.connect(self.newItemTriggered)
        self.actionNewAccountGroup.triggered.connect(self.newAccountGroupTriggered)
        self.actionDeleteItem.triggered.connect(self.deleteItemTriggered)
        self.actionEditItem.triggered.connect(self.editItemTriggered)
        self.actionMoveUp.triggered.connect(self.moveUpTriggered)
        self.actionMoveDown.triggered.connect(self.moveDownTriggered)
        self.actionDuplicateTransaction.triggered.connect(self.model.duplicate_item)
        self.actionUndo.triggered.connect(self.doc.model.undo)
        self.actionRedo.triggered.connect(self.doc.model.redo)
        
        # Open / Save / Import / Export / New
        self.actionNewDocument.triggered.connect(self.doc.new)
        self.actionOpenDocument.triggered.connect(self.doc.openDocument)
        self.actionOpenExampleDocument.triggered.connect(self.doc.openExampleDocument)
        self.actionImport.triggered.connect(self.doc.importDocument)
        self.actionSave.triggered.connect(self.doc.save)
        self.actionSaveAs.triggered.connect(self.doc.saveAs)
        self.actionExportToQIF.triggered.connect(self.doc.exportToQIF)
        
        # Misc
        self.actionNewTab.triggered.connect(self.model.new_tab)
        self.actionCloseTab.triggered.connect(self.closeTabTriggered)
        self.actionShowSelectedAccount.triggered.connect(self.model.show_account)
        self.actionNavigateBack.triggered.connect(self.navigateBackTriggered)
        self.actionJumpToAccount.triggered.connect(self.jumpToAccountTriggered)
        self.actionMakeScheduleFromSelected.triggered.connect(self.makeScheduleFromSelectedTriggered)
        self.actionReconcileSelected.triggered.connect(self.reconcileSelectedTriggered)
        self.actionToggleReconciliationMode.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionShowPreferences.triggered.connect(self.app.showPreferences)
        self.actionShowViewOptions.triggered.connect(self.app.showViewOptions)
        self.actionPrint.triggered.connect(self._print)
        self.actionShowHelp.triggered.connect(self.app.showHelp)
        self.actionRegister.triggered.connect(self.registerTriggered)
        self.actionCheckForUpdate.triggered.connect(self.checkForUpdateTriggered)
        self.actionAbout.triggered.connect(self.aboutTriggered)
        self.actionQuit.triggered.connect(self.close)
    
    #--- QWidget overrides
    def closeEvent(self, event):
        if self.doc.confirmDestructiveAction():
            event.accept()
        else:
            event.ignore()
    
    #--- Private
    def _print(self):
        dialog = QPrintDialog(self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        printer = dialog.printer()
        currentView = self.mainView.currentWidget()
        viewPrinter = ViewPrinter(printer, self.doc, currentView.PRINT_TITLE_FORMAT)
        currentView.fitViewsForPrint(viewPrinter)
        viewPrinter.render()
    
    def _savePrefs(self):
        self.app.prefs.mainWindowIsMaximized = self.isMaximized()
        self.app.prefs.mainWindowRect = self.geometry()
    
    def _setTabIndex(self, index):
        if not self.tabBar.count():
            return
        self.tabBar.setCurrentIndex(index)
        self._updateActionsState()
        pane_type = self.model.pane_type(index)
        view = None
        if pane_type == PaneType.NetWorth:
            view = self.nwview
        elif pane_type == PaneType.Profit:
            view = self.pview
        elif pane_type == PaneType.Transaction:
            view = self.tview
        elif pane_type == PaneType.Account:
            view = self.eview
        elif pane_type == PaneType.Schedule:
            view = self.scview
        elif pane_type == PaneType.Budget:
            view = self.bview
        elif pane_type == PaneType.Empty:
            view = self.newview
        self.mainView.setCurrentWidget(view)
        view.setFocus()
    
    def _updateActionsState(self):
        # Updates enable/disable checked/unchecked state of all actions. These state can change
        # under various conditions: main view change, date range type change and when reconciliation
        # mode is toggled
        
        # Determine what actions are enabled
        viewType = self.model.pane_type(self.model.current_pane_index)
        isSheet = viewType in (PaneType.NetWorth, PaneType.Profit)
        isTransactionOrEntryTable = viewType in (PaneType.Transaction, PaneType.Account)
        canToggleReconciliation = viewType == PaneType.Account and \
            self.eview.model.can_toggle_reconciliation_mode
        
        newItemLabel = {
            PaneType.NetWorth: "New Account",
            PaneType.Profit: "New Account",
            PaneType.Transaction: "New Transaction",
            PaneType.Account: "New Transaction",
            PaneType.Schedule: "New Schedule",
            PaneType.Budget: "New Budget",
            PaneType.Empty: "New Item", #XXX make disabled
        }[viewType]
        self.actionNewItem.setText(newItemLabel)
        self.actionNewAccountGroup.setEnabled(isSheet)
        self.actionMoveDown.setEnabled(isTransactionOrEntryTable)
        self.actionMoveUp.setEnabled(isTransactionOrEntryTable)
        self.actionDuplicateTransaction.setEnabled(isTransactionOrEntryTable)
        self.actionMakeScheduleFromSelected.setEnabled(isTransactionOrEntryTable)
        self.actionReconcileSelected.setEnabled(viewType == PaneType.Account and \
            self.eview.model.reconciliation_mode)
        self.actionShowNextView.setEnabled(self.model.current_pane_index < self.model.pane_count-1)
        self.actionShowPreviousView.setEnabled(self.model.current_pane_index > 0)
        self.actionShowSelectedAccount.setEnabled(isSheet or isTransactionOrEntryTable)
        self.actionNavigateBack.setEnabled(viewType == PaneType.Account)
        self.actionToggleReconciliationMode.setEnabled(canToggleReconciliation)
    
    def _updateUndoActions(self):
        if self.doc.model.can_undo():
            self.actionUndo.setEnabled(True)
            self.actionUndo.setText("Undo {0}".format(self.doc.model.undo_description()))
        else:
            self.actionUndo.setEnabled(False)
            self.actionUndo.setText("Undo")
        if self.doc.model.can_redo():
            self.actionRedo.setEnabled(True)
            self.actionRedo.setText("Redo {0}".format(self.doc.model.redo_description()))
        else:
            self.actionRedo.setEnabled(False)
            self.actionRedo.setText("Redo")
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        for i in xrange(self.mainView.count()):
            view = self.mainView.widget(i)
            if hasattr(view, 'updateOptionalWidgetsVisibility'):
                view.updateOptionalWidgetsVisibility()
    
    #--- Actions
    # Views
    def showNetWorthTriggered(self):
        self.model.select_balance_sheet()
    
    def showProfitLossTriggered(self):
        self.model.select_income_statement()
    
    def showTransactionsTriggered(self):
        self.model.select_transaction_table()
    
    def showSchedulesTriggered(self):
        self.model.select_schedule_table()
    
    def showBudgetsTriggered(self):
        self.model.select_budget_table()
    
    def showPreviousViewTriggered(self):
        self.model.select_previous_view()
    
    def showNextViewTriggered(self):
        self.model.select_next_view()
    
    # Document Edition
    def newItemTriggered(self):
        self.model.new_item()
    
    def newAccountGroupTriggered(self):
        self.model.new_group()
    
    def deleteItemTriggered(self):
        self.model.delete_item()
    
    def editItemTriggered(self):
        self.model.edit_item()
    
    def moveUpTriggered(self):
        self.model.move_up()
    
    def moveDownTriggered(self):
        self.model.move_down()
    
    # Misc
    def closeTabTriggered(self):
        self.model.close_pane(self.model.current_pane_index)
    
    def navigateBackTriggered(self):
        self.model.navigate_back()
    
    def jumpToAccountTriggered(self):
        self.model.jump_to_account()
    
    def makeScheduleFromSelectedTriggered(self):
        self.model.make_schedule_from_selected()
    
    def reconcileSelectedTriggered(self):
        self.eview.etable.model.toggle_reconciled()
    
    def toggleReconciliationModeTriggered(self):
        self.eview.model.toggle_reconciliation_mode()
    
    def registerTriggered(self):
        self.app.askForRegCode()
    
    def checkForUpdateTriggered(self):
        QProcess.execute('updater.exe', ['/checknow'])
    
    def aboutTriggered(self):
        self.app.showAboutBox()
    
    #--- Other Signals
    def currentTabChanged(self, index):
        self.model.current_pane_index = index
        self._setTabIndex(index)
    
    def tabCloseRequested(self, index):
        self.model.close_pane(index)
    
    def tabMoved(self, fromIndex, toIndex):
        self.model.move_pane(fromIndex, toIndex)
    
    #--- model --> view
    def change_current_pane(self):
        self._setTabIndex(self.model.current_pane_index)
    
    def refresh_panes(self):
        while self.tabBar.count() > 0:
            self.tabBar.removeTab(0)
        for i in xrange(self.model.pane_count):
            pane_label = self.model.pane_label(i)
            self.tabBar.addTab(pane_label)
    
    def refresh_undo_actions(self):
        self._updateUndoActions()
    
    def show_message(self, msg):
        title = "Warning"
        QMessageBox.warning(self, title, msg)
    
    def view_closed(self, index):
        self.tabBar.removeTab(index)
    
