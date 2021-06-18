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


def SpikesFromDB(sess, unit, coll):
    
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
    
    return v_dict, v_dict_sem, m_dict, m_dict_sem


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