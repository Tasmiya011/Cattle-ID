const DB_NAME = 'CattleID_Cache';
const DB_VERSION = 1;
let db = null;

function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => {
            db = request.result;
            resolve(db);
        };
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('cow_images')) {
                db.createObjectStore('cow_images', { keyPath: 'cow_id' });
            }
        };
    });
}

window.cacheCowImage = async (cowId, imageBase64) => {
    const db = await openIndexedDB();
    const tx = db.transaction(['cow_images'], 'readwrite');
    const store = tx.objectStore('cow_images');
    store.put({ cow_id: cowId, image: imageBase64, cached_at: Date.now() });
};

window.getCachedCowImage = async (cowId) => {
    const db = await openIndexedDB();
    const tx = db.transaction(['cow_images'], 'readonly');
    const store = tx.objectStore('cow_images');
    return new Promise((resolve, reject) => {
        const request = store.get(cowId);
        request.onsuccess = () => resolve(request.result ? request.result.image : null);
        request.onerror = () => reject(request.error);
    });
};