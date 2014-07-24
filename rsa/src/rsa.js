var B = require("bignum"),
    assert = require("assert");

// cheaply fixes JSON problems with BigNum
B.prototype.toJSON = function() {
    return this.toString();
};

var PubKey = function(n, e) {
    this.n = n;
    this.e = e;
};
PubKey.fromJSON = function(json) {
    var obj = JSON.parse(json);
    return new PubKey(obj.n, obj.e);
};
PubKey.prototype.encrypt = function(message) {
    return B(message).pow(this.e).mod(this.n);
};

var PrivKey = function(n, d) {
    this.n = n;
    this.d = d;
};
PrivKey.fromJSON = function(json) {
    var obj = JSON.parse(json);
    return new PrivKey(obj.n, obj.d);
};
PrivKey.prototype.decrypt = function(message) {
    return B(message).pow(this.d).mod(this.n);
};

var bezout = function(a, b) {
    var r = a, u = B(1), v = B(0), R = b, U = B(0), V = B(1), rt, ut, vt, q;
    a = B(a); b = B(b);
    while (! R.eq(0)) {
        q = (r.div(R));
        rt = r;               ut = u;               vt = v;
        r = R;                u = U;                v = V;
        R = rt.sub(q.mul(R)); U = ut.sub(q.mul(U)); V = vt.sub(q.mul(V));
    }
    return { r : r, u : u, v : v };
};

var genkeys = function(p, q, use_e) {
    var e, r, d, tuple;
    p = B(p); q = B(q);
    if (!use_e || use_e === 'default') {
        e = B(65537);
    } else if (use_e === 'random') {
        e = B.rand(65537);
    } else if (typeof use_e === 'number' || typeof use_e === 'string') {
        e = B(use_e);
    }
    r = p.sub(1).mul(q.sub(1));
    tuple = bezout(e, r);
    while(tuple.r != 1) {
        e = e.add(1);
        tuple = bezout(e, r);
    }
    n = q.mul(p);
    d = (tuple.u.lt(0) ? tuple.u : r.add(tuple.u));
    return {
        pubKey : new PubKey(n, e),
        privKey : new PrivKey(n, d)
    };
};

var genprime = function() {
    return B.rand(65537).add(65537).nextPrime();
};

var messageToBigNum = function(message) {
    return B([].map.call(message, function(x) {
        return ("000" + x.charCodeAt(0)).slice(-4);
    }).join(""));
};

var bigNumToMessage = function(bn) {
    return bn.toString().match(/([0-9]{4})/g).map(function(x) {
        return String.fromCharCode(parseInt(x, 10));
    }).join("");
};

exports.genkeys = genkeys;
exports.PrivKey = PrivKey;
exports.PubKey = PubKey;
exports.genprime = genprime;
exports.messageToBigNum = messageToBigNum;
exports.bigNumToMessage = bigNumToMessage;
