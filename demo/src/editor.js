var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/python");
editor.setShowPrintMargin(false);
editor.clearSelection();

var output = ace.edit("output");
output.renderer.$cursorLayer.element.style.display = 'none';
output.setTheme("ace/theme/chrome");
if(lang == 'js'){
    output.getSession().setMode("ace/mode/javascript");
} else if(lang == 'go'){
    output.getSession().setMode("ace/mode/golang");
}
output.setReadOnly(true);
output.setShowPrintMargin(false);
output.getSession().mergeUndoDeltas = true;
output.setHighlightActiveLine(false);      

editor.getSession().on('change', function(){
    output.setValue(generate(editor.getValue()));
    output.clearSelection();
    output.setHighlightActiveLine(false);
});
