# General imports
import numpy as np
import pickle
import hashlib
import json
import os

from utils.mongoUtils import MongoConnect, PullNHPs, PullSess, PullUnits, SpikesFromDB, MongoLogin, AllSDFs, UpdateUnit
from utils.plotUtils import PlotConds, PltMeanStd, PlotPop, GetYRange, AddVLine
from utils.mathUtils import NormSDFs

# Plotting imports
import plotly
import plotly.graph_objects as go

# Flask imports
from flask import Flask, render_template, request, jsonify, session, redirect
from flask.helpers import url_for

# Start app and clear session
app = Flask(__name__)
app.secret_key = 'secret2345'

# Open Mongo connection, starting with Guest
db = MongoConnect('guest', 'guest')
sdf_coll = db['preextracted_sdfs']

# Initialize figure dict
plot_conds = ['hh', 'hl', 'lh', 'll']
my_figs = {}
for i, v in enumerate(plot_conds):
    my_figs[v] = {}
    my_figs[v]['array'] = {}
    my_figs[v]['array']['data'] = []
    my_figs[v]['saccade'] = {}
    my_figs[v]['saccade']['data'] = []

# Initialize SST dict
sst_dict = {}

##############################
###### PAGES SECTION ######
##############################

# Route for landing page


@app.route('/')
def landing():
    # Check if logged in, otherwise redirect to login page
    is_auth = session.get('is_auth')
    if is_auth is False or is_auth is None:
        return redirect(url_for('login_page'))

    return render_template('home.html',
                           user=session['user'])


# Route for login page
@app.route('/login', methods=['POST', 'GET'])
def login_page():
    is_auth = session.get('is_auth')
    if is_auth:
        return redirect(url_for('landing'))
    return render_template('login.html')


# Route for checking individual SSTs
@app.route('/single-sst')
def single_sst():
    # Check if logged in, otherwise redirect to login page
    is_auth = session.get('is_auth')
    if is_auth is False or is_auth is None:
        session['user'] = 'none'

    # Make sst_dict a session variable
    session['sst_dict'] = sst_dict
    session['units_loaded'] = []

    # Make list of NHPs
    nhp_list = PullNHPs(sdf_coll, session['is_auth'])
    sess_list = PullSess(sdf_coll, nhp_list[0], session['is_auth'])
    unit_list = PullUnits(sdf_coll, sess_list[0], session['is_auth'])

    # Load initial spike/SDF values
    #v_dict, v_dict_sem, m_dict, m_dict_sem, unit_ssts = SpikesFromDB(sess_list[0], unit_list[0], sdf_coll, user=session['user'])

    # Make array-aligned figures
    for ic, cond in enumerate(plot_conds):
        my_figs[cond]['array']['data'] = json.dumps(
            go.Figure(), cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['array']['id'] = '{}-array'.format(cond)
        my_figs[cond]['saccade']['data'] = json.dumps(
            go.Figure(), cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['saccade']['id'] = '{}-sacc'.format(cond)

    return render_template('single_sst.html',
                           cond_plots=my_figs,
                           nhps=nhp_list,
                           sessions=sess_list,
                           units=unit_list,
                           logged_in=session['is_auth'])


# Page for looking at group averages
@app.route('/group-averages')
def group_averages():
    # First, we need to pull the units
    # pop_sdfs, unit_nhps = AllSDFs(sdf_coll, session['is_auth'])

    # Now generate the plots
    for ic, cond in enumerate(plot_conds):
        my_figs[cond]['array']['data'] = json.dumps(
            go.Figure(), cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['array']['id'] = '{}-array'.format(cond)
        my_figs[cond]['saccade']['data'] = json.dumps(
            go.Figure(), cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['saccade']['id'] = '{}-sacc'.format(cond)

    return render_template('population_sst.html',
                           cond_plots=my_figs,
                           logged_in=session['is_auth'])


##############################
###### CALLBACK SECTION ######
##############################

# Callback for login handling
@app.route('/login-cb', methods=['POST', 'GET'])
def login_callback():
    if request.args.get('buttonState') == 'Logout':
        is_auth = False
        session['is_auth'] = False
        session['user'] = 'none'
    else:
        uName = request.args.get('username')
        password_candidate = request.args.get('pwd')
        is_auth = session.get('is_auth')
        if is_auth is False or is_auth is None:
            is_auth = MongoLogin(db, uName, password_candidate)
            session['is_auth'] = is_auth
            if is_auth:
                session['user'] = uName
    session.modified = True

    return jsonify({'isAuth': is_auth})


# Callback for updating session list when NHP is changed
@app.route('/nhp-update-cb', methods=['POST', 'GET'])
def nhp_update_cb():
    nhp_list = PullNHPs(sdf_coll, session['is_auth'])
    if session['is_auth']:
        nhp_labs = [nhp_list[i] for i in range(len(nhp_list))]
    else:
        nhp_labs = [nhp_list[i][0:2] for i in range(len(nhp_list))]

    return jsonify({'nhpVals': nhp_list, 'nhpLabels': nhp_labs})


# Callback for updating session list when NHP is changed
@app.route('/sess-update-cb', methods=['POST', 'GET'])
def sess_update_cb():
    this_nhp = request.args.get('nhp')
    sess_list = PullSess(sdf_coll, this_nhp, session['is_auth'])

    return jsonify({'sessList': sess_list})


# Callback for updating unit list when session is changed
@app.route('/unit-update-cb', methods=['POST', 'GET'])
def unit_update_cb():
    this_sess = request.args.get('sess')
    unit_list = PullUnits(sdf_coll, this_sess, session['is_auth'])

    return jsonify({'unitList': unit_list})


@app.route('/set-quality-cb', methods=['POST', 'GET'])
def set_quality_cb():
    this_quality = request.args.get('quality')

    if session['session'] not in session['sst_dict'].keys():
        session['sst_dict'][session['session']] = {}
    if session['unit'] not in session['sst_dict'][session['session']].keys():
        session['sst_dict'][session['session']][session['unit']] = {}

    session['sst_dict'][session['session']
                        ][session['unit']]['Quality'] = this_quality
    session.modified = True

    return jsonify({'success': True})


@app.route('/set-type-cb', methods=['POST', 'GET'])
def set_type_cb():
    this_vm = request.args.get('vm')
    none_checked = request.args.get('none')

    if none_checked == 'true':
        this_vm = 0

    session['sst_dict'][session['session']
                        ][session['unit']]['VM_Score'] = this_vm
    session.modified = True

    return jsonify({'success': True})


@app.route('/get-scores-cb')
def get_scores():
    try:
        vm_val = session['sst_dict'][session['session']
                                     ][session['unit']]['VM_Score']
    except:
        session['sst_dict'][session['session']
                            ][session['unit']]['VM_Score'] = 3
        vm_val = 3

    try:
        qual_val = session['sst_dict'][session['session']
                                       ][session['unit']]['Quality']
    except:
        session['sst_dict'][session['session']][session['unit']]['Quality'] = 3
        qual_val = 3

    return jsonify({'vm': vm_val, 'qual': qual_val})


@app.route('/sst-click-cb', methods=['POST', 'GET'])
def sst_click_parse():
    click_sst = request.args.get('x')
    plot_id = request.args.get('plotID')
    sel_type = request.args.get('selType')
    if plot_id[3] == 'a':
        plot_label = plot_id[0:2]
    elif plot_id[3] == 's':
        plot_label = 'm'+plot_id[0:2]
    else:
        plot_label = 'unk'

    # Put in key dict
    if session['session'] not in session['sst_dict'].keys():
        session['sst_dict'][session['session']] = {}
    if session['unit'] not in session['sst_dict'][session['session']].keys():
        session['sst_dict'][session['session']][session['unit']] = {}
    if sel_type not in session['sst_dict'][session['session']][session['unit']].keys():
        session['sst_dict'][session['session']][session['unit']][sel_type] = {}
    if plot_label not in session['sst_dict'][session['session']][session['unit']][sel_type].keys():
        session['sst_dict'][session['session']
                            ][session['unit']][sel_type][plot_label] = []
    session['sst_dict'][session['session']][session['unit']
                                            ][sel_type][plot_label].append(click_sst)
    session.modified = True

    return jsonify({'success': True})


@app.route('/sst-submit', methods=['POST', 'GET'])
def sst_submit():
    # Save for backup security
    from random import randint
    f_name = './tmp_dict_{}.json'.format(randint(0, 1000000))
    with open(f_name, 'w') as w:
        json.dump(session['sst_dict'], w)

    # Now we can do the real update
    all_sess = session['sst_dict'].keys()
    n_tot = 0
    n_complete = 0
    for i, sess in enumerate(all_sess):
        sess_units = session['sst_dict'][sess].keys()
        for iu, unit in enumerate(sess_units):
            n_tot += 1
            update_dict = {}
            update_dict['ManualTimes_'+session['user']
                        ] = session['sst_dict'][sess][unit]
            update_success = UpdateUnit(sdf_coll, sess, unit, update_dict)
            if update_success:
                n_complete += 1
            else:
                print('Unable to update unit {} from session {}'.format(unit, sess))
    if n_tot == n_complete:
        os.remove(f_name)

    return jsonify({'success': True})


# Callback for updating plots
@app.route('/plot-update-cb', methods=['POST', 'GET'])
def update_plots():
    this_sess = request.args.get('sess')
    this_unit = request.args.get('unit')
    arr_x_min = request.args.get('aMinX')
    arr_x_max = request.args.get('aMaxX')
    sacc_x_min = request.args.get('sMinX')
    sacc_x_max = request.args.get('sMaxX')
    force_pull = request.args.get('forcePull')

    # This section should be used to prevent costly database queries, but it can't do that quite yet as v_dict etc. are local variables
    # Load spike/SDF values if the values are different
    if this_sess != session['session'] or this_unit != session['unit'] or force_pull == 'true':
        v_dict, v_dict_sem, m_dict, m_dict_sem, unit_ssts = SpikesFromDB(
            this_sess, this_unit, sdf_coll, user=session['user'])
        session['session'] = this_sess
        session['unit'] = this_unit
        if this_sess not in session['sst_dict'].keys():
            session['sst_dict'][session['session']] = {
                session['unit']: unit_ssts}
            session['units_loaded'].append(
                '{}-{}'.format(session['session'], session['unit']))
        elif this_unit not in session['sst_dict'][session['session']].keys():
            session['sst_dict'][session['session']][this_unit] = unit_ssts
            session['units_loaded'].append(
                '{}-{}'.format(session['session'], session['unit']))
        elif '{}-{}'.format(session['session'], session['unit']) not in session['units_loaded']:
            session['sst_dict'][session['session']
                                ][session['unit']] = unit_ssts
            session['units_loaded'].append(
                '{}-{}'.format(session['session'], session['unit']))
        elif '{}-{}'.format(session['session'], session['unit']) in session['units_loaded']:
            unit_ssts = session['sst_dict'][session['session']
                                            ][session['unit']]

        # If the unit gets loaded, initialize VM and Quality to 3 if they haven't been saved previously
        # (units that haven't been loaded will have no scores here and can be marked that way)
        if 'VM_Score' not in unit_ssts.keys():
            session['sst_dict'][session['session']
                                ][session['unit']]['VM_Score'] = 3
            session['sst_dict'][session['session']
                                ][session['unit']]['Quality'] = 3
        session.modified = True

        # Make array-aligned figures
        for ic, cond in enumerate(plot_conds):
            # Array plots
            tmp_fig = PlotConds(v_dict, v_dict_sem, cond)
            PlotConds(v_dict, v_dict_sem, cond[0]+'0', fig=tmp_fig)
            tmp_fig = AddVLine(
                tmp_fig, cond, session['sst_dict'][session['session']][session['unit']], mov=False)
            tmp_fig.update_layout(title='{}, Array Aligned'.format(cond.upper()),
                                  xaxis_range=[arr_x_min, arr_x_max],
                                  width=600, height=400,
                                  spikedistance=-1, hovermode='x unified'
                                  )
            my_figs[cond]['array']['data'] = json.dumps(
                tmp_fig, cls=plotly.utils.PlotlyJSONEncoder)
            my_figs[cond]['array']['id'] = '{}-array'.format(cond)

            # Saccade plots
            tmp_fig = PlotConds(m_dict, m_dict_sem, cond)
            PlotConds(m_dict, m_dict_sem, cond[0]+'0', fig=tmp_fig)
            tmp_fig = AddVLine(
                tmp_fig, cond, session['sst_dict'][session['session']][session['unit']], mov=True)
            tmp_fig.update_layout(title='{}, Saccade Aligned'.format(cond.upper()),
                                  xaxis_range=[sacc_x_min, sacc_x_max],
                                  width=600, height=400,
                                  spikedistance=-1, hovermode='x unified'
                                  )
            my_figs[cond]['saccade']['data'] = json.dumps(
                tmp_fig, cls=plotly.utils.PlotlyJSONEncoder)
            my_figs[cond]['saccade']['id'] = '{}-sacc'.format(cond)

        return my_figs
    else:
        return {'refresh': False}


# Make the query to the database to get the population SDF values
@app.route('/get-pop-plots', methods=['POST', 'GET'])
def get_pop_plots():
    arr_x_min = request.args.get('aMinX')
    arr_x_max = request.args.get('aMaxX')
    sacc_x_min = request.args.get('sMinX')
    sacc_x_max = request.args.get('sMaxX')

    # Pull the population data
    pop_sdfs, unit_nhps = AllSDFs(sdf_coll, session['is_auth'])

    # Normalize pop_sdfs for cross-unit scaling
    norm_sdfs = NormSDFs(pop_sdfs)

    # Now generate the plots
    for ic, cond in enumerate(plot_conds):
        # Array plots
        tmp_fig = PlotPop(norm_sdfs['Vis'], cond)
        PlotPop(norm_sdfs['Vis'], cond[0]+'0', fig=tmp_fig)
        tmp_fig.update_layout(title='{}, Array Aligned'.format(cond.upper()),
                              xaxis_range=[arr_x_min, arr_x_max],
                              width=600, height=400,
                              spikedistance=-1, hovermode='x unified'
                              )
        my_figs[cond]['array']['data'] = json.dumps(
            tmp_fig, cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['array']['id'] = '{}-array'.format(cond)

        # Saccade plots
        tmp_fig = PlotPop(norm_sdfs['Mov'], cond)
        PlotPop(norm_sdfs['Mov'], cond[0]+'0', fig=tmp_fig)
        tmp_fig.update_layout(title='{}, Saccade Aligned'.format(cond.upper()),
                              xaxis_range=[sacc_x_min, sacc_x_max],
                              width=600, height=400,
                              spikedistance=-1, hovermode='x unified'
                              )
        my_figs[cond]['saccade']['data'] = json.dumps(
            tmp_fig, cls=plotly.utils.PlotlyJSONEncoder)
        my_figs[cond]['saccade']['id'] = '{}-sacc'.format(cond)

    return my_figs


# Request to clear sst_dict for the displayed unit
@app.route('/clear-sst-cb', methods=['POST', 'GET'])
def clear_ssts():
    this_sess = request.args.get('sess')
    this_unit = request.args.get('unit')
    session['sst_dict'][this_sess][this_unit] = {}
    session.modified = True

    return jsonify({'success': True})


# Run the appP
if __name__ == '__main__':
    app.run(debug=True)
