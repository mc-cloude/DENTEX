use ic_cdk::export::candid::{CandidType, Deserialize};
use ic_cdk::storage;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, CandidType, Deserialize)]
pub struct Entitlement {
    pub tier: String,
    pub capabilities: Vec<String>,
}

type EntitlementStore = BTreeMap<String, Entitlement>;

#[ic_cdk::update]
pub fn put(partner: String, tier: String, capabilities: Vec<String>) {
    let entitlement = Entitlement { tier, capabilities };
    storage::get_mut::<EntitlementStore>().insert(partner, entitlement);
}

#[ic_cdk::query]
pub fn get(partner: String) -> Option<Entitlement> {
    storage::get::<EntitlementStore>().get(&partner).cloned()
}

#[ic_cdk::query]
pub fn proofs() -> Vec<Entitlement> {
    storage::get::<EntitlementStore>().values().cloned().collect()
}

#[ic_cdk::pre_upgrade]
fn pre_upgrade() {
    let data = storage::get::<EntitlementStore>();
    ic_cdk::storage::stable_save((data,)).expect("failed to save state");
}

#[ic_cdk::post_upgrade]
fn post_upgrade() {
    if let Ok((data,)) = ic_cdk::storage::stable_restore::<(EntitlementStore,)>() {
        *storage::get_mut::<EntitlementStore>() = data;
    }
}
