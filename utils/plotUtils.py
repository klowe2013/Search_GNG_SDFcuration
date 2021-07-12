import plotly.graph_objects as go
import numpy as np

def PltMeanStd(t, m, s, fig=None, color='rgb(0,0,0)', width = 10, name=None):
    
    if fig is None:
        fig = go.Figure()
    
    # Calculate upper and lower traces    
    upper = m + s
    lower = m - s
    t_cat = np.concatenate([t,t[::-1]])
    y_cat = np.concatenate([upper,lower[::-1]])
    fig.add_trace(go.Scatter(
        x=t_cat[np.isfinite(y_cat)],
        y=y_cat[np.isfinite(y_cat)],
        fill='toself',
        line=dict(color=color, width=0),
        name=name+'fill',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=t[np.isfinite(m)],
        y=m[np.isfinite(m)],
        line=dict(color=color, width=width),
        name=name,
        hoverinfo='x'
    ))


def PlotConds(mu_dict, sem_dict, cond, show_in=True, show_out=True, fig=None):    
    
    colors = {'hh': 'rgb(54, 54, 201)',
                   'hl': 'rgb(0, 0, 128)',
                   'lh': 'rgb(201, 54, 54)',
                   'll': 'rgb(128, 0, 0)',
                   'h0': 'rgb(54, 201, 201)',
                   'l0': 'rgb(201, 54, 201)'}
    
    IN_WIDTH = 3
    OUT_WIDTH = 1
        
    if fig is None:
        fig = go.Figure()
    
    if show_in:
        PltMeanStd(mu_dict['t'], mu_dict[cond]['in'], sem_dict[cond]['in'], fig=fig, color=colors[cond], width=IN_WIDTH, name=cond.upper()+' IN')
    if show_out:
        PltMeanStd(mu_dict['t'], mu_dict[cond]['out'], sem_dict[cond]['out'], fig=fig, color=colors[cond], width=OUT_WIDTH, name=cond.upper()+' OUT')
    
    return fig


def PlotPop(pop_sdfs, cond, show_in=True, show_out=True, fig=None):    
    
    import numpy as np
    
    colors = {'hh': 'rgb(54, 54, 201)',
                   'hl': 'rgb(0, 0, 128)',
                   'lh': 'rgb(201, 54, 54)',
                   'll': 'rgb(128, 0, 0)',
                   'h0': 'rgb(54, 201, 201)',
                   'l0': 'rgb(201, 54, 201)'}
    
    IN_WIDTH = 3
    OUT_WIDTH = 1

    if fig is None:
        fig = go.Figure()
    
    if show_in:
        PltMeanStd(pop_sdfs['Times'],
                   np.nanmean(pop_sdfs[cond.upper()]['in'],axis=0),
                   np.nanstd(pop_sdfs[cond.upper()]['in'],axis=0)/np.sqrt(pop_sdfs[cond.upper()]['in'].shape[0]),
                   fig=fig, color=colors[cond], width=IN_WIDTH, name=cond.upper()+' IN')
    if show_out:
        PltMeanStd(pop_sdfs['Times'],
                   np.nanmean(pop_sdfs[cond.upper()]['out'],axis=0),
                   np.nanstd(pop_sdfs[cond.upper()]['out'],axis=0)/np.sqrt(pop_sdfs[cond.upper()]['out'].shape[0]),
                   fig=fig, color=colors[cond], width=OUT_WIDTH, name=cond.upper()+' OUT')
    
    return fig


def GetYRange(fig):
    fig_data = fig.data
    
    min_y = min(min(list(map(lambda x: min(x.y), fig_data))),0.)
    max_y = max(list(map(lambda x: max(x.y), fig_data)))
    range_y = max_y-min_y
    
    return [min_y-(.05*range_y), max_y+(.05*range_y)]


def AddVLine(fig, cond, sst_dict, mov=False):
    # Define selection types
    sel_types = ['sst','cdt','msst']
    sel_colors = {'sst': 'rgb(54,201,54)', 'cdt': 'rgb(54, 201, 201)', 'ngsst': 'rgb(230, 147, 23)', 'outcdt': 'rgb(201, 201, 54)', 'unk': 'rgb(0,0,0)'};
    # Get Y lim
    y_range = GetYRange(fig)
    
    for it, sel in enumerate(sel_types):
        if sel[0]=='m' and mov==False:
            continue
        if sel[0]!='m' and mov==True:
            continue
        if sel in sst_dict.keys() and cond in sst_dict[sel].keys():
            these_ssts = sst_dict[sel][cond]
            if type(these_ssts) is str:
                these_ssts = [these_ssts]
            for ii, t_val in enumerate(these_ssts):
                try:
                    fig.add_trace(go.Scatter(
                    x=[int(t_val),int(t_val)],
                    y=y_range,
                    line=dict(color=sel_colors[sel]),
                    name=sel+'_'+str(ii),
                    visible=True
                    ))
                except:
                    pass
    fig.update_layout(yaxis_range=y_range)
    
    return fig