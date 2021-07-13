const term = new Terminal();
term.open(document.getElementById("terminal"));
term.write(" machine $ ");
term.onKey(function(key, event) {
    console.log(key.charCodeAt(0));
    console.log(event.keyCode);
});

prompt = () => {
    var shellprompt = "$ ";
    term.write("\r\n" + shellprompt);
};;