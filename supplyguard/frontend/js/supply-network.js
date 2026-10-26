// Independent, browser-only digital supply network simulator.
const seedInventory = [
  { sku: 'NS-1042', product: 'Edge gateway', category: 'Hardware', onHand: 128, reserved: 42, reorderAt: 60, supplier: 'Northstar Components', leadDays: 4 },
  { sku: 'NS-2088', product: 'Secure sensor kit', category: 'IoT', onHand: 46, reserved: 28, reorderAt: 50, supplier: 'Aster Electronics', leadDays: 6 },
  { sku: 'NS-3310', product: 'Fiber uplink module', category: 'Networking', onHand: 214, reserved: 61, reorderAt: 80, supplier: 'Meridian Optics', leadDays: 3 },
  { sku: 'NS-4417', product: 'Power control unit', category: 'Hardware', onHand: 19, reserved: 12, reorderAt: 35, supplier: 'Aster Electronics', leadDays: 8 },
  { sku: 'NS-5521', product: 'Telemetry node', category: 'IoT', onHand: 92, reserved: 30, reorderAt: 45, supplier: 'BluePeak Systems', leadDays: 5 },
];
const seedShipments = [
  { id: 'SHP-80421', supplier: 'Northstar Components', destination: 'New York DC', items: 48, eta: 1, status: 'In transit', risk: 'On track' },
  { id: 'SHP-80422', supplier: 'Aster Electronics', destination: 'Austin DC', items: 36, eta: 2, status: 'In transit', risk: 'On track' },
  { id: 'SHP-80423', supplier: 'Meridian Optics', destination: 'Seattle DC', items: 72, eta: 3, status: 'Preparing', risk: 'On track' },
  { id: 'SHP-80424', supplier: 'BluePeak Systems', destination: 'New York DC', items: 24, eta: 4, status: 'In transit', risk: 'On track' },
];
const copy = value => JSON.parse(JSON.stringify(value));
const time = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
const escaped = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));

export const supplyNetwork = {
  inventory: copy(seedInventory),
  shipments: copy(seedShipments),
  suppliers: [
    { name: 'Northstar Components', score: 98, status: 'Healthy', region: 'US · Ohio' },
    { name: 'Aster Electronics', score: 84, status: 'Healthy', region: 'TW · Hsinchu' },
    { name: 'Meridian Optics', score: 96, status: 'Healthy', region: 'DE · Munich' },
    { name: 'BluePeak Systems', score: 91, status: 'Healthy', region: 'US · Oregon' },
  ],
  events: [
    { kind: 'success', title: 'Network simulator ready', detail: 'Inventory, supplier, and shipment feeds connected', when: 'Just now' },
    { kind: 'info', title: 'Shipment SHP-80421 dispatched', detail: 'Northstar Components → New York DC · 48 units', when: '2 min ago' },
    { kind: 'success', title: 'Purchase order PO-22904 confirmed', detail: 'Meridian Optics · 72 fiber uplink modules', when: '5 min ago' },
  ],
  running: true,
  ticks: 0,
  onHandTotal() { return this.inventory.reduce((sum, item) => sum + item.onHand, 0); },
  atRiskCount() { return this.inventory.filter(item => item.onHand - item.reserved <= item.reorderAt).length; },
  delayedCount() { return this.shipments.filter(item => item.risk === 'Delayed').length; },
  event(title, detail, kind = 'info') {
    this.events.unshift({ kind, title, detail, when: time() });
    this.events = this.events.slice(0, 20);
  },
  tick() {
    if (!this.running) return;
    this.ticks++;
    if (this.ticks % 2 === 0) {
      const moving = this.shipments.filter(item => item.status === 'In transit');
      if (moving.length) {
        const shipment = moving[this.ticks % moving.length];
        if (shipment.eta > 0) shipment.eta--;
        if (shipment.eta === 0 && shipment.risk !== 'Delayed') {
          shipment.status = 'Arrived';
          shipment.risk = 'Delivered';
          const related = this.inventory.find(item => item.supplier === shipment.supplier);
          if (related) related.onHand += shipment.items;
          this.event(`Shipment ${shipment.id} received`, `${shipment.supplier} → ${shipment.destination} · ${shipment.items} units received`, 'success');
        } else this.event(`Shipment ${shipment.id} checkpoint`, `Transit scan received · ETA ${shipment.eta} day${shipment.eta === 1 ? '' : 's'} · Mock carrier API`, 'info');
      } else this.event('Demand forecast refreshed', 'Regional demand model recalculated · mock telemetry', 'info');
    }
  },
  action(action) {
    if (action === 'pause') { this.running = !this.running; return this.running ? 'Live supply events resumed.' : 'Live supply events paused.'; }
    if (action === 'reset') {
      this.inventory = copy(seedInventory); this.shipments = copy(seedShipments); this.ticks = 0; this.running = true;
      this.suppliers.forEach(supplier => { supplier.status = 'Healthy'; });
      this.events = [{ kind:'success', title:'Supply network reset', detail:'Sample inventory, suppliers, and shipments restored', when:time() }];
      return 'Supply network simulation reset.';
    }
    if (action === 'shortage') {
      const item = this.inventory.find(product => product.sku === 'NS-4417');
      item.onHand = Math.max(0, item.onHand - 8);
      this.event('Inventory shortage detected', `${item.product} fell below reorder point · ${item.onHand} units available`, 'critical');
      return `${item.product} inventory reduced; reorder threshold alert raised.`;
    }
    if (action === 'delay') {
      const shipment = this.shipments.find(item => item.status === 'In transit' && item.risk !== 'Delayed');
      if (!shipment) return 'No in-transit shipment is available to delay. Reset the simulation and try again.';
      shipment.eta += 3; shipment.risk = 'Delayed';
      this.event(`Shipment ${shipment.id} delayed`, `Carrier exception · ETA moved by 3 days · ${shipment.destination}`, 'warning');
      return `Shipment ${shipment.id} delayed by three simulated days.`;
    }
    if (action === 'supplier') {
      const supplier = this.suppliers.find(item => item.name === 'Aster Electronics');
      supplier.status = 'At risk'; supplier.score = 62;
      const related = this.shipments.find(item => item.supplier === supplier.name && item.status === 'In transit');
      if (related) { related.eta += 2; related.risk = 'Delayed'; }
      this.event('Supplier risk alert', `${supplier.name} capacity fell 35% · alternate sourcing recommended`, 'critical');
      return `${supplier.name} disruption simulated; affected orders flagged for sourcing review.`;
    }
    if (action === 'receipt') {
      const item = this.inventory.find(product => product.sku === 'NS-4417');
      item.onHand += 24;
      this.event('Emergency replenishment received', `${item.product} +24 units · expedited purchase order PO-22908`, 'success');
      return 'Emergency replenishment received and inventory updated.';
    }
    return '';
  },
};

function pill(text, type) { return `<span class="badge ${type}"><i></i>${escaped(text)}</span>`; }
function stockLevel(item) {
  const available = item.onHand - item.reserved;
  return available <= item.reorderAt ? ['Low stock', 'critical'] : available <= item.reorderAt * 1.4 ? ['Reorder soon', 'warning'] : ['Healthy', 'healthy'];
}
function actionButton(text, action, cls = 'btn small secondary') { return `<button class="${cls}" data-supply-action="${action}">${text}</button>`; }

export function supplyNetworkMini() {
  const atRisk = supplyNetwork.atRiskCount();
  return `<div class="supply-mini"><div class="supply-mini-stats"><div><b>${supplyNetwork.onHandTotal().toLocaleString()}</b><small>units on hand</small></div><div><b>${supplyNetwork.shipments.filter(s=>s.status==='In transit').length}</b><small>shipments moving</small></div><div><b>${atRisk}</b><small>items need attention</small></div></div><div class="supply-mini-line"><span class="supply-live-dot"></span><span>${atRisk ? `${atRisk} stock alert${atRisk===1?'':'s'} need review` : 'Inventory and shipments on track'}</span><button data-page="Supply Network Simulator">Open network →</button></div></div>`;
}

export function supplyNetworkPage() {
  const s = supplyNetwork;
  const atRisk = s.atRiskCount();
  const delivered = s.shipments.filter(item => item.status === 'Arrived').length;
  const supplierRisk = s.suppliers.filter(item => item.status !== 'Healthy').length;
  const stats = [
    ['TOTAL ON HAND', s.onHandTotal().toLocaleString(), `${s.inventory.length} tracked SKUs`, '▦'],
    ['IN TRANSIT', s.shipments.filter(item => item.status === 'In transit').length, `${s.delayedCount()} delayed shipments`, '⇢'],
    ['STOCK ALERTS', atRisk, atRisk ? 'Reorder point reached' : 'All above reorder point', '!'],
    ['SUPPLIER HEALTH', `${s.suppliers.length - supplierRisk}/${s.suppliers.length}`, supplierRisk ? `${supplierRisk} supplier risk alert` : 'All partners healthy', '⬡'],
  ];
  return `<div class="page-heading"><div><div class="eyebrow">DIGITAL SUPPLY CHAIN · SIMULATION</div><h1>Supply network simulator</h1><p>Follow inventory, supplier capacity, purchase orders, and shipments as events unfold in real time.</p></div><div class="heading-actions">${actionButton(s.running?'Ⅱ Pause live feed':'▶ Resume live feed','pause','btn secondary')}${actionButton('↻ Reset','reset','btn quiet')}</div></div>
    <div class="stat-grid">${stats.map((item,i)=>`<article class="stat-card"><div class="stat-top"><span>${item[0]}</span><i class="stat-icon ${i===2?'amber':''}">${item[3]}</i></div><strong>${item[1]}</strong><small>${item[2]}</small></article>`).join('')}</div>
    <div class="supply-controls"><div><span class="supply-live-dot ${s.running?'':'paused'}"></span><b>${s.running?'LIVE SIMULATION':'SIMULATION PAUSED'}</b><small>Events advance every few seconds · all records are mock data</small></div><div>${actionButton('⚠ Simulate shortage','shortage','btn small danger')}${actionButton('⇢ Simulate shipment delay','delay','btn small secondary')}${actionButton('⬡ Supplier disruption','supplier','btn small secondary')}${actionButton('+ Receive replenishment','receipt','btn small primary')}</div></div>
    <div class="supply-layout"><section class="panel"><div class="panel-head"><div><h2>Inventory by SKU</h2><p>Available stock compared with reorder point</p></div>${pill(atRisk?`${atRisk} NEED ATTENTION`:'STOCK HEALTHY',atRisk?'warning':'healthy')}</div><div class="table-wrap"><table><thead><tr><th>PRODUCT</th><th>SKU</th><th>ON HAND</th><th>RESERVED</th><th>AVAILABLE</th><th>REORDER AT</th><th>STATUS</th></tr></thead><tbody>${s.inventory.map(item=>{const available=item.onHand-item.reserved;const [label,type]=stockLevel(item);return `<tr><td><b>${escaped(item.product)}</b><small>${escaped(item.category)} · ${escaped(item.supplier)}</small></td><td class="mono">${escaped(item.sku)}</td><td>${item.onHand}</td><td>${item.reserved}</td><td><b>${available}</b><div class="stock-meter"><i class="${type}" style="width:${Math.max(4,Math.min(100,available/item.reorderAt*34))}%"></i></div></td><td>${item.reorderAt}</td><td>${pill(label,type)}</td></tr>`}).join('')}</tbody></table></div></section>
    <section class="panel"><div class="panel-head"><div><h2>Supplier scorecard</h2><p>Capacity, score, and simulated region</p></div>${pill(supplierRisk?'RISK DETECTED':'4 PARTNERS','healthy')}</div><div class="supplier-list">${s.suppliers.map(item=>`<div class="supplier-row"><span class="supplier-mark">${escaped(item.name.slice(0,1))}</span><span class="supplier-detail"><b>${escaped(item.name)}</b><small>${escaped(item.region)}</small></span><span class="supplier-score">${item.score}<small>/100</small></span>${pill(item.status.toUpperCase(),item.status==='Healthy'?'healthy':'critical')}</div>`).join('')}</div></section>
    <section class="panel supply-wide"><div class="panel-head"><div><h2>Shipment tracking</h2><p>Carrier events · estimated arrival · mock logistics feed</p></div>${pill(`${s.shipments.length} SHIPMENTS`,'running')}</div><div class="table-wrap"><table><thead><tr><th>SHIPMENT</th><th>SUPPLIER</th><th>DESTINATION</th><th>UNITS</th><th>ETA</th><th>STATUS</th><th>RISK</th></tr></thead><tbody>${s.shipments.map(item=>`<tr><td><b>${escaped(item.id)}</b><small>Carrier sync · updated ${escaped(s.events[0]?.when||'now')}</small></td><td>${escaped(item.supplier)}</td><td>${escaped(item.destination)}</td><td>${item.items}</td><td>${item.status==='Arrived'?'Delivered':`${item.eta} day${item.eta===1?'':'s'}`}</td><td>${pill(item.status.toUpperCase(),item.status==='Arrived'?'healthy':item.status==='Preparing'?'pending':'running')}</td><td>${pill(item.risk.toUpperCase(),item.risk==='Delayed'?'warning':item.risk==='Delivered'?'healthy':'healthy')}</td></tr>`).join('')}</tbody></table></div></section>
    <section class="panel"><div class="panel-head"><div><h2>Live supply events</h2><p>Inventory changes, supplier alerts, and delivery scans</p></div><span class="live-label"><i></i> ${s.running?'STREAMING':'PAUSED'}</span></div><div class="supply-events">${s.events.slice(0,8).map(event=>`<div class="activity-row"><span class="activity-icon ${event.kind==='success'?'healthy':event.kind==='critical'?'critical':'blue'}">${event.kind==='critical'?'!':event.kind==='success'?'✓':'›'}</span><span class="activity-copy"><b>${escaped(event.title)}</b><small>${escaped(event.detail)}</small></span><time>${escaped(event.when)}</time></div>`).join('')}</div></section>
    <section class="panel"><div class="panel-head"><div><h2>Order fulfillment</h2><p>How demand flows through the network</p></div>${pill('MOCK FORECAST','running')}</div><div class="fulfillment"><div class="fulfillment-ring"><span>${Math.max(72,96-atRisk*6-s.delayedCount()*9)}<small>%</small></span></div><div><b>Projected on-time fulfillment</b><small>Based on available stock, supplier lead time, and shipment ETAs.</small><div class="fulfillment-note">${delivered} shipments delivered in this simulation</div></div></div></section></div>`;
}
