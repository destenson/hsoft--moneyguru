/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGTable2.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"

@interface MGEditableTable2 : MGTable2
{
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
}
- (id)initWithModel:(PyTable2 *)aPy tableView:(NSTableView *)aTableView;
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(NSTableView *)aTableView;
/* Virtual */
- (NSArray *)dateColumns;
- (NSArray *)completableColumns;
/* Public */
- (void)startEditing;
- (void)stopEditing;
- (NSString *)editedFieldname;
- (id)fieldEditorForObject:(id)asker;
@end