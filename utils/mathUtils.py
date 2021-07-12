import numpy as np
import numpy.matlib

def NormSDFs(in_sdfs):
    
    GOOD_CONDS = ['HH','HL','LH','LL','H0','L0']
    BL_WIND = [-300,-100]
    
    # Concatenate Vis and Mov conditions, full trials
    io_cat_all = np.concatenate(
        [np.concatenate(
            (in_sdfs['Vis'][cond]['in'],
            in_sdfs['Vis'][cond]['out'],
            in_sdfs['Mov'][cond]['out'],
            in_sdfs['Mov'][cond]['out'])
            ,axis=1) 
        for i, cond in enumerate(GOOD_CONDS)]
    ,axis=1)
    unit_sigma = np.nanstd(io_cat_all,axis=1)
    
    # Concatenate Vis conditions, just baseline period
    io_cat_bl = np.concatenate(
        [np.concatenate(
            (in_sdfs['Vis'][cond]['in'][:,np.in1d(in_sdfs['Vis']['Times'],np.arange(BL_WIND[0],BL_WIND[1]))],
             in_sdfs['Vis'][cond]['out'][:,np.in1d(in_sdfs['Vis']['Times'],np.arange(BL_WIND[0],BL_WIND[1]))])
            ,axis=1)
        for i, cond in enumerate(GOOD_CONDS)]
    ,axis=1)
    unit_bl_mean = np.nanmean(io_cat_bl,axis=1)
    
    for i, cond in enumerate(GOOD_CONDS):
        # Use vis baseline and overall sigma to Z-score
        bl_mat = np.matlib.repmat(unit_bl_mean,in_sdfs['Vis'][cond]['in'].shape[1],1).transpose()
        sig_mat = np.matlib.repmat(unit_sigma,in_sdfs['Vis'][cond]['in'].shape[1],1).transpose()
        in_vis = (in_sdfs['Vis'][cond]['in'] - bl_mat) / sig_mat
        out_vis = (in_sdfs['Vis'][cond]['out'] - bl_mat) / sig_mat
        in_sdfs['Vis'][cond] = {'in': in_vis, 'out': out_vis}
        
        bl_mat = np.matlib.repmat(unit_bl_mean,in_sdfs['Mov'][cond]['in'].shape[1],1).transpose()
        sig_mat = np.matlib.repmat(unit_sigma,in_sdfs['Mov'][cond]['in'].shape[1],1).transpose()
        in_mov = (in_sdfs['Mov'][cond]['in'] - bl_mat) / sig_mat
        out_mov = (in_sdfs['Mov'][cond]['out'] - bl_mat) / sig_mat
        in_sdfs['Mov'][cond] = {'in': in_mov, 'out': out_mov}
    
    return in_sdfs