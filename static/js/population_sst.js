// Hide unchecked values
function hideUnchecked() {
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
        for (ia = 0; ia < arrNames.length; ia++) {
            thisPlot = document.getElementById(arrNames[ia]);
            visIndices = []
            invisIndices = []
            // Loop through children of this plot
            for (i = 0; i < thisPlot.data.length; i++) {
                if (Object.keys(thisPlot.data[i]).includes('type')) {
                    // Check if this is "in-go"
                    if (thisPlot.data[i].name[1] !== '0' && thisPlot.data[i].name[3] === 'I') {
                        // Check if "in-go" is checked
                        if (inGoCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            visIndices.push(i)
                        } else if (!inGoCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            invisIndices.push(i)
                        }
                    }
                    // Check if this is "out-go"
                    if (thisPlot.data[i].name[1] !== '0' && thisPlot.data[i].name[3] === 'O') {
                        // Check if "out-go" is checked
                        if (outGoCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            visIndices.push(i)
                        } else if (!outGoCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            invisIndices.push(i)
                        }
                    }
                    // Check if this is "in-no-go"
                    if (thisPlot.data[i].name[1] === '0' && thisPlot.data[i].name[3] === 'I') {
                        // Check if "out-go" is checked
                        if (inNgCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            visIndices.push(i)
                        } else if (!inNgCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            invisIndices.push(i)
                        }
                    }
                    // Check if this is "out-no-go"
                    if (thisPlot.data[i].name[1] === '0' && thisPlot.data[i].name[3] === 'O') {
                        // Check if "out-go" is checked
                        if (outNgCheck && (!thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            visIndices.push(i)
                        } else if (!outNgCheck && (thisPlot.data[i].visible || typeof thisPlot.data[i].visible === 'undefined')) {
                            invisIndices.push(i)
                        }
                    }
                }
            }
            if (visIndices.length > 0) {
                Plotly.restyle(thisPlot, { 'visible': true }, visIndices);
            }
            if (invisIndices.length > 0) {
                Plotly.restyle(thisPlot, { 'visible': false }, invisIndices);
            }
        }
        resolve();
    })
}

function updateClickEvents() {
    return new Promise((resolve, reject) => {
        let allPlots = {};
        var i;
        for (i = 0; i < arrNames.length; i++) {
            allPlots[arrNames[i]] = document.getElementById(arrNames[i]);
            // Initialize on-click listeners
            allPlots[arrNames[i]].on('plotly_click', (data, i) => {
                // Get the X value
                const thisX = data['points'][0]['x'];
                // Get this element
                const thisPlot = data['event']['path'][6]['id'];
                // Try to infer what type of selection point this is
                const selType = inferSelection();

                // Get the layout of thisPlot
                let thisY = document.getElementById(thisPlot).layout.yaxis.range;
                Plotly.addTraces(document.getElementById(thisPlot), { x: [thisX, thisX], y: thisY, line: { 'color': selTypeColors[selType] } });
                Plotly.relayout(document.getElementById(thisPlot), { 'yaxis.range': thisY });
            })
        }
        resolve();
    })
}

function submitSSTs() {
    $.getJSON({
        url: "/sst-submit", data: { 'submit': true }, success: (res) => {
            console.log('Successfully submitted SST')
        }
    })
}

// When unit changes we don't want to automatically reload, but when "Update" is sent we do want to re-pull the plots
function updatePopPlots(rePull) {
    // Get the current state of the session and units (NHP isn't necessary because it's redundant with session)
    const aMinX = document.getElementById('array_xmin_state').value
    const aMaxX = document.getElementById('array_xmax_state').value
    const sMinX = document.getElementById('sacc_xmin_state').value
    const sMaxX = document.getElementById('sacc_xmax_state').value

    return new Promise((resolve, reject) => {
        if (rePull) {
            updateButton.value = 'Requesting data...'
            $.getJSON({
                url: "/get-pop-plots", data: { 'aMinX': aMinX, 'aMaxX': aMaxX, 'sMinX': sMinX, 'sMaxX': sMaxX }, success: (res) => {
                    var keys = Object.keys(res);
                    updateButton.value = 'Parsing Input...';
                    var i;
                    for (i = 0; i < keys.length; i++) {
                        var arrGraphs = JSON.parse(res[keys[i]].array.data);
                        var saccGraphs = JSON.parse(res[keys[i]].saccade.data);
                        Plotly.react(res[keys[i]].array.id, arrGraphs, {});
                        Plotly.react(res[keys[i]].saccade.id, saccGraphs, {});
                    }
                    resolve();
                }
            });
        } else {
            updateButton.value = 'Fixing Axes...'
            let arrUpdate = { 'xaxis.range': [aMinX, aMaxX] };
            let saccUpdate = { 'xaxis.range': [sMinX, sMaxX] };
            const arrPlots = Array.from(document.getElementsByClassName('arr-plot'))
            arrPlots.forEach((item) => {
                Plotly.relayout(item, arrUpdate);
            })
            const saccPlots = Array.from(document.getElementsByClassName('sacc-plot'))
            saccPlots.forEach((item) => {
                Plotly.relayout(item, saccUpdate);
            })
            //updateButton.value = 'Fixing Traces...';
            resolve();
        }

    })


    //hideUnchecked();
    //updateButton.value = 'Update';
}

function inferSelection() {
    const inGoChecked = document.getElementById('in-go').checked;
    const outGoChecked = document.getElementById('out-go').checked;
    const inNgChecked = document.getElementById('in-ng').checked;
    const outNgChecked = document.getElementById('out-ng').checked;

    let selType = '';
    // Basic two options are SST and CDT
    if (inGoChecked && outGoChecked && !inNgChecked) {
        selType = 'sst';
    } else if (inGoChecked && !outGoChecked && inNgChecked) {
        selType = 'cdt';
    } else if (!inGoChecked && !outGoChecked && inNgChecked && outNgChecked) {
        selType = 'ngsst';
    } else if (!inGoChecked && outGoChecked && !inNgChecked && outNgChecked) {
        selType = 'outcdt';
    } else {
        selType = 'unk';
    }
    return selType;
}

function logout() {
    $.getJSON({
        url: "/login-cb", data: { 'buttonState': 'Logout' }, success: () => {
            window.location.href = "/login";
        }
    })
}
// Attach update function to page load
window.onload = () => {
    updatePopPlots(true).then(() => {
        updateClickEvents().then(() => {
            hideUnchecked().then(() => updateButton.value = 'Update')
        })
    })
}

// Set global variables
const arrNames = ["hh-array", "hl-array", "lh-array", "ll-array", "hh-sacc", "hl-sacc", "lh-sacc", "ll-sacc"];
const selTypeColors = { 'sst': 'rgb(54,201,54)', 'cdt': 'rgb(54, 201, 201)', 'ngsst': 'rgb(230, 147, 23)', 'outcdt': 'rgb(201, 201, 54)', 'unk': 'rgb(0,0,0)' };
const updateButton = document.getElementById('plots_update');
updateButton.addEventListener('click', () => {
    updatePopPlots(false).then(() => {
        hideUnchecked().then(() => updateButton.value = 'Update')
    })
})

// Hide initially unchecked values
//hideUnchecked();
//updateClickEvents();