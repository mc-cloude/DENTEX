use ic_cdk::export::candid::{CandidType, Deserialize};
use ic_cdk::storage;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, CandidType, Deserialize)]
pub struct ConsentRecord {
    pub scope: String,
    pub granted_at: u64,
    pub revoked_at: Option<u64>,
    pub signer: String,
}

type ConsentStore = BTreeMap<String, ConsentRecord>;

#[ic_cdk::update]
pub fn grant(scope: String, signer: String, timestamp: u64) {
    let record = ConsentRecord {
        scope: scope.clone(),
        granted_at: timestamp,
        revoked_at: None,
        signer,
    };
    storage::get_mut::<ConsentStore>().insert(scope, record);
}

#[ic_cdk::update]
pub fn revoke(scope: String, timestamp: u64) {
    if let Some(record) = storage::get_mut::<ConsentStore>().get_mut(&scope) {
        record.revoked_at = Some(timestamp);
    }
}

#[ic_cdk::query]
pub fn get(scope: String) -> Option<ConsentRecord> {
    storage::get::<ConsentStore>().get(&scope).cloned()
}

#[ic_cdk::query]
pub fn proofs() -> Vec<ConsentRecord> {
    storage::get::<ConsentStore>().values().cloned().collect()
}

#[ic_cdk::pre_upgrade]
fn pre_upgrade() {
    let data = storage::get::<ConsentStore>();
    ic_cdk::storage::stable_save((data,)).expect("failed to save state");
}

#[ic_cdk::post_upgrade]
fn post_upgrade() {
    if let Ok((data,)) = ic_cdk::storage::stable_restore::<(ConsentStore,)>() {
        *storage::get_mut::<ConsentStore>() = data;
    }
}
