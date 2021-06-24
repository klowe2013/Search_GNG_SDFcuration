def MongoConnect(user,pwd):
    
    from pymongo import MongoClient
    import urllib

    userParse = urllib.parse.quote_plus(user)
    pwdParse = urllib.parse.quote_plus(pwd)
    client = MongoClient("mongodb+srv://{}:{}@kalebclusterdev.1fjuw.mongodb.net/KalebClusterDev?retryWrites=true&w=majority".format(userParse,pwdParse))
    db = client['sdfs_database']
    
    return db


def PullNHPs(coll, is_auth):
    # Get all sessions and units to get distinct NHPs
    if is_auth:
        all_docs = coll.find({},{'Session': 1, 'Unit': 1})
    else:
        all_docs = coll.find({'GuestAccess': True},{'Session': 1, 'Unit': 1})
    all_nhp = all_docs.distinct('NHP')
    
    return all_nhp


def PullSess(coll, my_nhp, is_auth):
    # Get all sessions and units from "my_nhp"
    if is_auth:
        all_docs = coll.find({'NHP': my_nhp},{'Session': 1, 'Unit': 1})
    else:
        all_docs = coll.find({'NHP': my_nhp, 'GuestAccess': True}, {'Session': 1, 'Unit': 1})
    nhp_sess = all_docs.distinct('Session')    
    
    return nhp_sess


def PullUnits(coll, my_sess, is_auth):
    # Get all sessions and units from "my_nhp"
    if is_auth:
        all_docs = coll.find({'Session': my_sess},{'Session': 1, 'Unit': 1})
    else:
        all_docs = coll.find({'Session': my_sess, 'GuestAccess': True}, {'Session': 1, 'Unit': 1})
    nhp_sess = all_docs.distinct('Unit')    
    
    return nhp_sess


def SpikesFromDB(sess, unit, coll, user=None):
    
    import pickle

    query = {'Session': sess, 'Unit': unit}
    doc = coll.find_one(query)
    
    my_conds = ['HH','HL','LH','LL','H0','L0']
    v_dict = {}
    m_dict = {}
    v_dict_sem = {}
    m_dict_sem = {}
    for i in range(len(my_conds)):
        v_dict[my_conds[i].lower()] = {'in': pickle.loads(doc[my_conds[i]]['InV']), 'out': pickle.loads(doc[my_conds[i]]['OutV'])}
        v_dict_sem[my_conds[i].lower()] = {'in': pickle.loads(doc[my_conds[i]]['InVS']), 'out': pickle.loads(doc[my_conds[i]]['OutVS'])}
        if '0' not in my_conds[i]:
            m_dict[my_conds[i].lower()] = {'in': pickle.loads(doc[my_conds[i]]['InM']), 'out': pickle.loads(doc[my_conds[i]]['OutM'])}
            m_dict_sem[my_conds[i].lower()] = {'in': pickle.loads(doc[my_conds[i]]['InMS']), 'out': pickle.loads(doc[my_conds[i]]['OutMS'])}
    v_dict['t'] = pickle.loads(doc['vTimes'])        
    v_dict_sem['t'] = pickle.loads(doc['vTimes'])        
    m_dict['t'] = pickle.loads(doc['mTimes'])        
    m_dict_sem['t'] = pickle.loads(doc['mTimes'])        
    
    if user is None:
        sst_dict = {}
    else:
        sst_dict = doc['ManualTimes_'+user]
    
    return v_dict, v_dict_sem, m_dict, m_dict_sem, sst_dict


def AllSDFs(coll, auth):
    
    import pickle
    import numpy as np
    
    query = {}
    
    if not auth:
        query['GuestAccess'] = True
    
    docs = coll.find(query) # Later, we'll add a 'Good' field so we can pull just the good units, or use a rating scale. For now, pull all
    n_docs = coll.count_documents(query)
    
    # Initialize Outputs
    my_conds = ['HH','HL','LH','LL','H0','L0']
    all_sdfs = {'Vis': {}, 'Mov': {}}
    all_times = {}
    nhp = []
    for ic, cond in enumerate(my_conds):
        all_sdfs['Vis'][cond] = {}
        all_sdfs['Mov'][cond] = {}
        all_sdfs['Vis'][cond]['in'] = [[] for i in range(n_docs)]
        all_sdfs['Vis'][cond]['out'] = [[] for i in range(n_docs)]
        if cond[1] is not '0': # For now there are no Mov aligned NOGO trials
            all_sdfs['Mov'][cond]['in'] = [[] for i in range(n_docs)]
            all_sdfs['Mov'][cond]['out'] = [[] for i in range(n_docs)]
            
    for id, doc in enumerate(docs):
        for ic, cond in enumerate(my_conds):
            all_sdfs['Vis'][cond]['in'][id] = pickle.loads(doc[cond]['InV'])
            all_sdfs['Vis'][cond]['out'][id] = pickle.loads(doc[cond]['OutV'])
            if cond[1] is not '0': # For now there are no Mov aligned NOGO trials
                all_sdfs['Mov'][cond]['in'][id] = pickle.loads(doc[cond]['InM'])
                all_sdfs['Mov'][cond]['out'][id] = pickle.loads(doc[cond]['OutM'])
        if id==0:
            all_sdfs['Vis']['Times'] = pickle.loads(doc['vTimes'])
            all_sdfs['Mov']['Times'] = pickle.loads(doc['mTimes'])
            
        nhp.append(doc['NHP'])
    
    # Now convert to np arrays
    for ic, cond in enumerate(my_conds):
        all_sdfs['Vis'][cond]['in'] = np.array(all_sdfs['Vis'][cond]['in'])
        all_sdfs['Vis'][cond]['out'] = np.array(all_sdfs['Vis'][cond]['out'])
        if cond[1] is not '0':
            all_sdfs['Mov'][cond]['in'] = np.array(all_sdfs['Mov'][cond]['in'])
            all_sdfs['Mov'][cond]['out'] = np.array(all_sdfs['Mov'][cond]['out'])
    
    return all_sdfs, nhp
        

def MongoLogin(db, user_in, pass_in):
    import hashlib

    is_auth = False
    # If user_in or pass_in are empty strings, don't bother checking the password
    if user_in=='' or pass_in=='' or pass_in is None:
        pass
    else:
        user_coll = db['UserAuth']
        hashed_pass = hashlib.sha256(pass_in.encode()).hexdigest()
        if hashed_pass == user_coll.find_one({'User': user_in},{'Password': 1})['Password']:
            is_auth = True
            
    return is_auth    


def UpdateUnit(coll, sess, unit, update):
    query = {'Session': sess, 'Unit': unit}
    # Now do the update
    success = True
    try:
        coll.update_one(query, {"$set": update})
    except:
        success = False
    return success