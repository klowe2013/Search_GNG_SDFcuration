// Manage NHP list
function getNHPs(){
    $.getJSON({
        url: "/nhp-update-cb", success: (res) => {
            updateNHPList(res.nhpVals, res.nhpLabels);
        }
    })
}

function updateNHPList(vals, labels){
    // Start by removing all options
    const nhpOpts = document.querySelectorAll('#nhp-dropdown option');
    nhpOpts.forEach(o => o.remove());
    
    const nhpDropDown = document.getElementById('nhp-dropdown');
    var i;
    for (i = 0; i < vals.length; i++) {
        var opt = document.createElement('option');
        opt.value = vals[i];
        opt.innerHTML = labels[i];
        nhpDropDown.appendChild(opt);
    }
    getSessList(vals[0]);
}

// Manage session list
function getSessList(nhp){
    // Request from backend by sending nhp value
    $.getJSON({
        url: "/sess-update-cb", data: {'nhp': nhp}, success: (res) => {
            updateSessList(res.sessList);
        }
    })
}

// Update session list in the DOM
function updateSessList(sessList){
    // Start by removing all options
    const sessOpts = document.querySelectorAll('#sess-dropdown option');
    sessOpts.forEach(o => o.remove());
    
    const sessDropDown = document.getElementById('sess-dropdown');
    var i;
    for (i = 0; i < sessList.length; i++) {
        var opt = document.createElement('option');
        opt.value = sessList[i];
        opt.innerHTML = sessList[i].split('-')[1];
        sessDropDown.appendChild(opt);
    }
    getUnitList(sessList[0])
}

// Get the unit list from a given session
function getUnitList(session){
    // Request from backend by sending session value
    $.getJSON({
        url: "/unit-update-cb", data: {'sess': session}, success: (res) => {
            updateUnitList(res.unitList);
        }
    })
}

// Update unit dropdown in the DOM
function updateUnitList(unitList){
    // Start by removing all options
    const unitOpts = document.querySelectorAll('#unit-dropdown option');
    unitOpts.forEach(o => o.remove());
    
    const unitDropDown = document.getElementById('unit-dropdown');
    var i;
    for (i = 0; i < unitList.length; i++) {
        var opt = document.createElement('option');
        opt.value = unitList[i];
        opt.innerHTML = unitList[i];
        unitDropDown.appendChild(opt);
    }
}

// Hide unchecked values
function hideUnchecked(){
    console.log('Entering hideUnchecked')
    // Get checked elements
    const inGoCheck = document.getElementById("in-go").checked;
    const outGoCheck = document.getElementById("out-go").checked;
    const inNgCheck = document.getElementById("in-ng").checked;
    const outNgCheck = document.getElementById("out-ng").checked;

    updateButton.value = 'Fixing conditions...'
    return new Promise((resolve, reject) => {
        // Loop over array plots
        var ia, i;
        let thisPlot;
        let visIndices = []
        let invisIndices = []
        for (ia=0; ia < arrNames.length; ia++){
            thisPlot = document.getElementById(arrNames[ia]);
            visIndices = []
            invisIndices = []
            // Loop through children of this plot
            for (i=0; i < thisPlot.data.length; i++){
                if (Object.keys(thisPlot.data[i]).includes('type')){
                    // Check if this is "out-go"
                    if (thisPlot.data[i].name[1] !== '0' && thisPlot.data[i].name[3] === 'O'){
                        // Check if "out-go" is checked
                        if (outGoCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            visIndices.push(i)
                        } else if (!outGoCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            invisIndices.push(i)
                        }
                    }
                    // Check if this is "in-no-go"
                    if (thisPlot.data[i].name[1] === '0' && thisPlot.data[i].name[3] === 'I'){
                        // Check if "out-go" is checked
                        if (inNgCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            visIndices.push(i)
                        } else if (!inNgCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            invisIndices.push(i)
                        }
                    }
                    // Check if this is "out-no-go"
                    if (thisPlot.data[i].name[1] === '0' && thisPlot.data[i].name[3] === 'O'){
                        // Check if "out-go" is checked
                        if (outNgCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            visIndices.push(i)
                        } else if (!outNgCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            invisIndices.push(i)
                        }
                    }
                    // If name is "sst", check if both "in-go" and "out-go" are checked
                    if (thisPlot.data[i].name.slice(0,3) === 'sst'){
                        if (inGoCheck && outGoCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            visIndices.push(i)
                        } else if ((!inGoCheck || !outGoCheck ) && (thisPlot.data[i].visible ||  typeof thisPlot.data[i].visible === 'undefined')){
                            invisIndices.push(i)
                        }
                    }
                    // If name is "cdt", check if both "in-go" and "in-nogo" are checked
                    if (thisPlot.data[i].name.slice(0,3) === 'cdt'){
                        if (inGoCheck && inNgCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')){
                            visIndices.push(i)
                        } else if ((!inGoCheck || !inNgCheck ) && (thisPlot.data[i].visible ||  typeof thisPlot.data[i].visible === 'undefined')){
                            invisIndices.push(i)
                        }
                    }
                }
            }
            if (visIndices.length > 0){
                Plotly.restyle(thisPlot, {'visible': true}, visIndices);
            }
            if (invisIndices.length > 0){
                Plotly.restyle(thisPlot, {'visible': false}, invisIndices);
            }
        }
        resolve();
    })    
}

function updateClickEvents(){
    let allPlots = {};
    var i;
    for (i=0; i< arrNames.length; i++){
        allPlots[arrNames[i]] = document.getElementById(arrNames[i]);
        // Initialize on-click listeners
        allPlots[arrNames[i]].on('plotly_click', (data, i) =>{
            // Get the X value
            const thisX = data['points'][0]['x'];
            // Get this element
            const thisPlot = data['event']['path'][6]['id'];
            // Try to infer what type of selection point this is
            const selType = inferSelection();
            // Send to sst-click
            $.getJSON({
                url: "/sst-click-cb", data: {'x': thisX, 'plotID': thisPlot, 'selType': selType}, success: (res) => {
                    // Get the layout of thisPlot
                    let thisY = document.getElementById(thisPlot).layout.yaxis.range;
                    Plotly.addTraces(document.getElementById(thisPlot), {x: [thisX, thisX], y: thisY, line: {'color': selTypeColors[selType]}});
                    Plotly.relayout(document.getElementById(thisPlot), {'yaxis.range': thisY});
                }
            })
        })
    }
}

function submitSSTs(){
    $.getJSON({
        url: "/sst-submit", data: {'submit': true}, success: (res) => {
            console.log('Successfully submitted SST')
        }
    })
}

// When unit changes we don't want to automatically reload, but when "Update" is sent we do want to re-pull the plots
function updateSessPlots(forcePull){
    // Get the current state of the session and units (NHP isn't necessary because it's redundant with session)
    const sessValue = document.getElementById('sess-dropdown').value
    const unitValue = document.getElementById('unit-dropdown').value
    const aMinX = document.getElementById('array_xmin_state').value
    const aMaxX = document.getElementById('array_xmax_state').value
    const sMinX = document.getElementById('sacc_xmin_state').value
    const sMaxX = document.getElementById('sacc_xmax_state').value

    return new Promise( (resolve, reject) => {
        updateButton.value = 'Requesting...'
        $.getJSON({
            url: "/plot-update-cb", data: {'sess': sessValue, 'unit': unitValue, 'aMinX': aMinX, 'aMaxX': aMaxX, 'sMinX': sMinX, 'sMaxX': sMaxX, 'forcePull': forcePull}, success: (res) => {
                var keys = Object.keys(res);
                console.log(res)
                // If the session and unit are the same (i.e., we're just updating axis range and check conditions), res returns {'refresh': False}
                if (keys[0]==='refresh'){
                    updateButton.value = 'Fixing Axes...'
                    let arrUpdate = {'xaxis.range': [aMinX, aMaxX]};
                    let saccUpdate = {'xaxis.range': [sMinX, sMaxX]};
                    const arrPlots = Array.from(document.getElementsByClassName('arr-plot'))
                    arrPlots.forEach((item) => {
                        Plotly.relayout(item, arrUpdate);
                    })
                    const saccPlots = Array.from(document.getElementsByClassName('sacc-plot'))
                    saccPlots.forEach((item) => {
                        Plotly.relayout(item, saccUpdate);
                    })
                    resolve();
                } else {
                    updateButton.value = 'Parsing Input...';
                    var i;
                    for (i=0; i < keys.length; i++){
                        var arrGraphs = JSON.parse(res[keys[i]].array.data);
                        var saccGraphs = JSON.parse(res[keys[i]].saccade.data);
                        Plotly.react(res[keys[i]].array.id, arrGraphs, {});  
                        Plotly.react(res[keys[i]].saccade.id, saccGraphs, {});  
                    }
                    resolve();
                }
            }
        })
    })
    
}

function inferSelection(){
    const inGoChecked = document.getElementById('in-go').checked;
    const outGoChecked = document.getElementById('out-go').checked;
    const inNgChecked = document.getElementById('in-ng').checked;
    const outNgChecked = document.getElementById('out-ng').checked;

    let selType = '';
    // Basic two options are SST and CDT
    if (inGoChecked && outGoChecked && !inNgChecked){
        selType = 'sst';
    } else if (inGoChecked && !outGoChecked && inNgChecked){
        selType = 'cdt';
    } else if (!inGoChecked && !outGoChecked && inNgChecked && outNgChecked){
        selType = 'ngsst';
    } else if (!inGoChecked && outGoChecked && !inNgChecked && outNgChecked){
        selType = 'ocdt';
    } else{
        selType = 'unk';
    }
    return selType;
}

function clearSSTs(){
    // Later we'll want to make this more dynamic (give options to clear...), but for now resetting all will work
    const sessValue = document.getElementById('sess-dropdown').value
    const unitValue = document.getElementById('unit-dropdown').value
    
    document.getElementById('sst_clear').value = 'Clearing SSTs...'
    
    $.getJSON({
        url: "/clear-sst-cb", data: {'sess': sessValue, 'unit': unitValue}, success: (res) => {
            document.getElementById('sst_clear').value = 'Clear Selection Times'
            const arrPlots = Array.from(document.getElementsByClassName('arr-plot'))
            const saccPlots = Array.from(document.getElementsByClassName('sacc-plot'))
            arrPlots.forEach((item) => {
                // Item.data contains lines
                let itemData = item.data;
                // Pull line names from data
                let names = itemData.map((line) => line.name);
                let delTraces = []
                names.forEach((o,i) => {
                    if (selTypes.includes(o.slice(0,3))){
                        delTraces.push(i)
                    }
                })
                Plotly.deleteTraces(item,delTraces)
            })
            saccPlots.forEach((item) => {
                // Item.data contains lines
                let itemData = item.data;
                // Pull line names from data
                let names = itemData.map((line) => line.name);
                let delTraces = []
                names.forEach((o,i) => {
                    if (selTypes.includes(o.slice(0,3))){
                        delTraces.push(i)
                    }
                })
                Plotly.deleteTraces(item,delTraces)
            })
        }
    })
}

function logout(){
    $.getJSON({
        url: "/login-cb", data: {'buttonState': 'Logout'}, success: () => {
            window.location.href = "/login";
        }
    })
}

// Attach update function to page load
window.onload = () => {
    updateSessPlots(true).then(()=>{
        hideUnchecked().then(() => updateButton.value = 'Update')
    })
}

// Set global variables
const arrNames = ["hh-array", "hl-array", "lh-array", "ll-array","hh-sacc", "hl-sacc", "lh-sacc", "ll-sacc"];
const selTypeColors = {'sst': 'rgb(54,201,54)', 'cdt': 'rgb(54, 201, 201)', 'ngsst': 'rgb(230, 147, 23)', 'ocdt': 'rgb(201, 201, 54)', 'unk': 'rgb(0,0,0)'};
const selTypes = ['sst','cdt','ngs','ocd','unk']

// Add event listeners for NHP and Session dropdowns
const nhpElement = document.getElementById('nhp-dropdown')
const sessElement = document.getElementById('sess-dropdown')
const updateButton = document.getElementById('plots_update');
nhpElement.addEventListener("change", (e) => {
    getSessList(e.target.value)
})
sessElement.addEventListener("change", (e) => {
    getUnitList(e.target.value)
})
updateButton.addEventListener('click', () => {
    updateSessPlots(false).then(()=>{
        hideUnchecked().then(() => updateButton.value = 'Update')
    })
})    

// Hide initially unchecked values
updateClickEvents();
