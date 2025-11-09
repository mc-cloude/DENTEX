use ic_cdk::export::candid::{CandidType, Deserialize, Principal};
use ic_cdk::storage;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, CandidType, Deserialize)]
pub struct Anchor {
    pub anchor_id: String,
    pub tenant: String,
    pub created_at: u64,
}

type AnchorStore = BTreeMap<Principal, Anchor>;

#[ic_cdk::update]
pub fn register(anchor_id: String, tenant: String, timestamp: u64) {
    let principal = ic_cdk::caller();
    let anchor = Anchor {
        anchor_id,
        tenant,
        created_at: timestamp,
    };
    storage::get_mut::<AnchorStore>().insert(principal, anchor);
}

#[ic_cdk::query]
pub fn get(principal: Principal) -> Option<Anchor> {
    storage::get::<AnchorStore>().get(&principal).cloned()
}

#[ic_cdk::query]
pub fn proofs() -> Vec<Anchor> {
    storage::get::<AnchorStore>().values().cloned().collect()
}

#[ic_cdk::pre_upgrade]
fn pre_upgrade() {
    let data = storage::get::<AnchorStore>();
    ic_cdk::storage::stable_save((data,)).expect("failed to save state");
}

#[ic_cdk::post_upgrade]
fn post_upgrade() {
    if let Ok((data,)) = ic_cdk::storage::stable_restore::<(AnchorStore,)>() {
        *storage::get_mut::<AnchorStore>() = data;
    }
}
