function checkBrowserVer(){
    var nVer = navigator.appVersion;
    var nAgt = navigator.userAgent;
    var browserName  = navigator.appName;
    var fullVersion  = ''+parseFloat(navigator.appVersion);
    var majorVersion = parseInt(navigator.appVersion,10);
    var nameOffset,verOffset,ix;
    var validBrowser = false;
    // In Opera, the true version is after "Opera" or after "Version"
    if ((verOffset=nAgt.indexOf("Opera"))!=-1) {
        browserName = "Opera";
        fullVersion = nAgt.substring(verOffset+6);
        if ((verOffset=nAgt.indexOf("Version"))!=-1)
            fullVersion = nAgt.substring(verOffset+8);
    }
    // In MSIE, the true version is after "MSIE" in userAgent
    else if ((verOffset=nAgt.indexOf("MSIE"))!=-1) {
        browserName = "Microsoft Internet Explorer";
        fullVersion = nAgt.substring(verOffset+5);
    }
    // In Chrome, the true version is after "Chrome"
    else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
        browserName = "Chrome";
        fullVersion = nAgt.substring(verOffset+7);
        validBrowser = true;
    }
    // In Safari, the true version is after "Safari" or after "Version"
    else if ((verOffset=nAgt.indexOf("Safari"))!=-1) {
        browserName = "Safari";
        fullVersion = nAgt.substring(verOffset+7);
        if ((verOffset=nAgt.indexOf("Version"))!=-1)
            fullVersion = nAgt.substring(verOffset+8);
        }
    // In Firefox, the true version is after "Firefox"
    else if ((verOffset=nAgt.indexOf("Firefox"))!=-1) {
        browserName = "Firefox";
        fullVersion = nAgt.substring(verOffset+8);
        validBrowser = true;
    }
    // In most other browsers, "name/version" is at the end of userAgent
    else if ( (nameOffset=nAgt.lastIndexOf(' ')+1) <
            (verOffset=nAgt.lastIndexOf('/')) )
    {
        browserName = nAgt.substring(nameOffset,verOffset);
        fullVersion = nAgt.substring(verOffset+1);
        if (browserName.toLowerCase()==browserName.toUpperCase()) {
            browserName = navigator.appName;
        }
    }
    // trim the fullVersion string at semicolon/space if present
    if ((ix=fullVersion.indexOf(";"))!=-1)
        fullVersion=fullVersion.substring(0,ix);
    if ((ix=fullVersion.indexOf(" "))!=-1)
        fullVersion=fullVersion.substring(0,ix);

    majorVersion = parseInt(''+fullVersion,10);
    if (isNaN(majorVersion)) {
        fullVersion  = ''+parseFloat(navigator.appVersion);
        majorVersion = parseInt(navigator.appVersion,10);
    }
    if (validBrowser){
        msg = "Valid browser!";
    }
    else{
        msg = "You are using " + browserName + ", please use Chrome or Firefox!";
    }
    console.log(msg);
    return msg;
}

async function background(source){
    try {
        const {results, error} = await asyncRun(source);
        if (results) {
            console.log('pyodideWorker return results: ', results);
            if (Array.isArray(results)){
              updateEditor(results);
            }
            else{
                console.log(results)
                updateError(results);
            }
        } else if (error) {
            updateError(error);
            console.log('pyodideWorker error: ', error);
        }
    }
    catch (e){
        console.log(`Error in pyodideWorker at ${e.filename}, Line: ${e.lineno}, ${e.message}`)
    }
}


function convert(input) {
    output = document.getElementById('output');
    output.innerHTML = '';
    MathJax.texReset();
    var options = MathJax.getMetricsFor(output);
    options.display = 1;
    MathJax.tex2chtmlPromise(input, options).then(function (node) {
        output.appendChild(node);
        MathJax.startup.document.clear();
        MathJax.startup.document.updateDocument();
    }).catch(function (err) {
        output.appendChild(document.createElement('pre')).appendChild(document.createTextNode(err.message));
    }).then(function () {
    });
}

function updateEditor(code) {
    var cpp = ace.edit("cpp");
    cpp.session.setValue(code[1]);
    var python = ace.edit("python");
    python.session.setValue(code[0]);
    var latex = ace.edit("latex");
    latex.session.setValue(code[2]);
    convert(code[3]);
    // reset UI
    document.getElementById("submit_icon").className = "fa fa-refresh";
    document.getElementById("compile").disabled = false;
}

function updateError(err) {
    console.log(err);
    showMsg(err);
    document.getElementById("submit_icon").className = "fa fa-refresh";
    document.getElementById("compile").disabled = false;
}

function compileFunction(){
    var iheartla = ace.edit("editor");
    var source = iheartla.getValue();
    console.log(source)
    pythonCode = `
import iheartla.la_parser.parser
source_code = r"""${source}"""
iheartla.la_parser.parser.compile_la_content(source_code)
`
    background(pythonCode);
    console.log("code")
}

function clickCompile(){
    try {
        document.getElementById("submit_icon").className = "fa fa-refresh fa-spin";
        document.getElementById("compile").disabled = true;
        compileFunction();
    } catch (error) {
        console.error(error);
        document.getElementById("submit_icon").className = "fa fa-refresh";
        document.getElementById("compile").disabled = false;
    }
    finally {
    }
}

function showMsg(msg){
    document.getElementById("msg").hidden = false;
    document.getElementById("msg").innerHTML = msg;
    setTimeout(function(){ document.getElementById("msg").hidden = true; document.getElementById("msg").innerHTML = ''; }, 2000);
}

function onEditIhla(e){
    console.log('edit'+e)
    var editor = ace.edit("editor");
    editor.find('\\R');
    editor.replaceAll('ℝ');
}

