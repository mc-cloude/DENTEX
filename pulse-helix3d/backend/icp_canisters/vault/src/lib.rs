use ic_cdk::export::candid::{CandidType, Deserialize};
use ic_cdk::storage;
use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, CandidType, Deserialize)]
pub struct VaultPointer {
    pub key_id: String,
    pub expires_at: Option<u64>,
}

type VaultStore = BTreeMap<String, VaultPointer>;

#[ic_cdk::update]
pub fn put(key: String, pointer: VaultPointer) {
    storage::get_mut::<VaultStore>().insert(key, pointer);
}

#[ic_cdk::query]
pub fn get(key: String) -> Option<VaultPointer> {
    storage::get::<VaultStore>().get(&key).cloned()
}

#[ic_cdk::query]
pub fn proofs() -> Vec<VaultPointer> {
    storage::get::<VaultStore>().values().cloned().collect()
}

#[ic_cdk::pre_upgrade]
fn pre_upgrade() {
    let data = storage::get::<VaultStore>();
    ic_cdk::storage::stable_save((data,)).expect("failed to save state");
}

#[ic_cdk::post_upgrade]
fn post_upgrade() {
    if let Ok((data,)) = ic_cdk::storage::stable_restore::<(VaultStore,)>() {
        *storage::get_mut::<VaultStore>() = data;
    }
}
