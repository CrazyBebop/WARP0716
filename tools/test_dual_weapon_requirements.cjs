// Patch-time contract tests only; no game/GPU acceptance or generated artifacts.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'Scripts/Patches/AllowDualWeaponSprites.qjs'), 'utf8');
assert.match(source, /const DualWeaponStatic =/);
const retiredName = 'AllowDual' + 'CustomWeaponSprites';
assert.equal(fs.existsSync(path.join(root, 'Scripts/Patches', retiredName + '.qjs')), false);
assert.equal(source.includes(retiredName), false);
assert.equal(fs.readFileSync(path.join(root, 'Patches/Special.yml'), 'utf8').includes(retiredName), false);
let files = {}, active = new Set(), inputs = {}, reads = 0, closes = 0;
let image = Buffer.alloc(0x5000);
const context = vm.createContext({
  RagexeClientProfile: {Id: 20250716},
  Warp: {Path: root, TgtExe: 'C:/client/Ragnarok.exe', GetPatchState: name => active.has(name)},
  System: {DirPath: () => 'C:/client'}, CODE: 1,
  TextFile: class {
    constructor(name) { this.lines = files[name]?.split(/\r?\n/); this.index = 0; }
    get Valid() { return Boolean(this.lines); }
    AtEnd() { return this.index >= this.lines.length; }
    ReadLine() { return this.lines[this.index++]; }
    Close() { closes++; }
  },
  BinFile: class {
    constructor(name) { this.name = name; }
    get Valid() { return this.name in files; }
    Close() { closes++; }
  },
  Exe: {
    GetSavedInput: name => inputs[name],
    Vir2Phy: value => value === 0xDB98B6 ? 0 : value >= 0x2000000 && value < 0x2005000 ? value - 0x2000000 : -1,
    Phy2Vir: value => value === 0 ? 0xDB98B6 : value + 0x2000000,
    GetUint8: value => { reads++; return image.readUInt8(value); },
    GetUint32: value => { reads++; return image.readUInt32LE(value); },
    GetInt32: value => { reads++; return image.readInt32LE(value); },
    GetText: value => image.subarray(value, image.indexOf(0, value)).toString(),
  },
});
vm.runInContext(source, context);
const run = expression => vm.runInContext(expression, context);
assert.equal(run('typeof ' + retiredName), 'undefined');
assert.match(source, /PatchDiagnostics\.add\("AllowDualWeaponSprites\.AuthoredRig"/);
assert.equal(run('AllowDualWeaponSprites.validate()'), true);
assert.equal(run('typeof ' + retiredName), 'undefined');
context.RagexeClientProfile.Id = 20260219;
assert.equal(run('AllowDualWeaponSprites.validate()'), false);
context.RagexeClientProfile.Id = 20250716;
const check = () => run('DualWeaponStatic.assertArchives()');
const archive = 'dual_weapon_male_assets.grf';
files['C:/client/' + archive] = '';
inputs.$inpMultGRF = 'C:/lists/embedded.ini';
files[inputs.$inpMultGRF] = '[Data]\n0=' + archive + '\n1=data.grf';
assert.equal(Array.from(run('DualWeaponStatic.readArchiveList("C:/lists/embedded.ini", true)'))[0], archive);
files['C:/client/DATA.INI'] = '[Data]\n0=' + archive;
delete files[inputs.$inpMultGRF];
assert.throws(() => run('DualWeaponStatic.readArchiveList("C:/lists/embedded.ini", true)'), /not readable/);
active = new Set(['GRFsFromIni']); inputs.$dataINI = 'DATA.INI';
check();
files['C:/client/DATA.INI'] = '[Other]\n0=' + archive + '\n[Data]\n0=data.grf';
assert.throws(check, /mount .* first/);
files['C:/client/DATA.INI'] = '[Data]\n0=./DUAL_WEAPON_MALE_ASSETS.GRF\n1=data.grf';
files['C:/client/./DUAL_WEAPON_MALE_ASSETS.GRF'] = '';
check(); delete files['C:/client/./DUAL_WEAPON_MALE_ASSETS.GRF'];
assert.throws(check, /copy dual_weapon_male_assets/);

// Reopened already-patched input: build exactly MultiGRFs' CALL-over-string ABI.
function embedded(names, corrupt = false) {
  image.fill(0); image[0] = 0xE8; image.writeInt32LE(0x2000100 - 0xDB98BB, 1);
  let offset = 0x100;
  for (const name of [...names].reverse()) {
    const length = Buffer.byteLength(name) + 1;
    image[offset] = 0xE8; image.writeInt32LE(length, offset + 1);
    image.write(name, offset + 5); offset += 5 + length;
    image[offset] = 0xB9; image.writeUInt32LE(0x159D410, offset + 1);
    image[offset + 5] = 0xE8;
    image.writeInt32LE(0xA88890 - (0x2000000 + offset + 10), offset + 6);
    offset += 10;
  }
  image[offset] = corrupt ? 0x90 : 0xC3;
}
active = new Set(); embedded([archive, 'data.grf']); check();
embedded(['data.grf', archive]); assert.throws(check, /mount .* first/);
assert.throws(check, /DATA.INI does not override/);
active = new Set(); embedded([archive, 'data.grf']); check();
embedded([archive, 'data.grf'], true); assert.throws(check, /cannot verify/);
image.fill(0); image[0] = 0xE8; image.writeInt32LE(0xA88890 - 0xDB98BB, 1);
assert.throws(check, /using GRFsEmbedded or GRFsFromIni/);

console.log('PASS single canonical patch/export, retired wrapper/catalog absent, profile validation, embedded/INI mount order, missing files and reopened/malformed loaders; no files generated.');