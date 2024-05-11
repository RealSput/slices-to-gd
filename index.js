require('@g-js-api/g.js');
let slices = require('./lines.json');
let offset = 10 * 3;
// x_pos, y_pos, x_scale, rot
// obj id 507
let dot = unknown_g();
$.add({
	OBJ_ID: 1764,
	X: 15,
	Y: 15,
	GROUPS: dot
})
dot.lock_to_player(true, false);
slices.forEach((lines, i) => {
	// further = front
	// earlier = back
	let other_g = unknown_g();
	lines.forEach(x => {
		let [x_pos, y_pos, x_scale, rot] = x;
		$.add({
			OBJ_ID: 507, // 503
			X: (x_pos * 100) + offset,
			Y: (y_pos * 100),
			SCALE_X: x_scale * 4,
			ROTATION: rot,
			Z_ORDER: i,
			LINKED_GROUP: i + 1,
			COLOR: color(2),
			HVS_ENABLED: true,
			EDITOR_LAYER_1: i,
			HVS: `0a1a${100 / (slices.length - i)}a0a0`,
			GROUPS: other_g
		});
	});
	other_g.follow(dot, 1 / (slices.length - i) * 10)
});
$.liveEditor({ info: true });