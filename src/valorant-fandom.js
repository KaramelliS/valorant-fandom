/*!
 * valorant-fandom v1.0.0
 * Valorant Fandom Wiki veri kutuphanesi
 * https://github.com/hzKamburga/valorant-fandom
 * MIT License
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.ValorantFandom = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var BASE_URL = 'https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data';
  var _cache = {};

  function _fetch(url) {
    if (_cache[url]) return Promise.resolve(_cache[url]);
    return fetch(url)
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(data) {
        _cache[url] = data;
        return data;
      });
  }

  function _setBaseUrl(url) {
    BASE_URL = url.replace(/\/+$/, '');
    _cache = {};
  }

  function getAgents() {
    return _fetch(BASE_URL + '/agents.json');
  }

  function getWeapons() {
    return _fetch(BASE_URL + '/weapons.json');
  }

  function getMaps() {
    return _fetch(BASE_URL + '/maps.json');
  }

  function getSkins(weaponName) {
    return _fetch(BASE_URL + '/skins.json').then(function(all) {
      if (weaponName) {
        return all[weaponName] || [];
      }
      return all;
    });
  }

  function getRanks(tier) {
    return _fetch(BASE_URL + '/ranks.json').then(function(ranks) {
      if (tier) {
        return ranks.filter(function(r) {
          return r.tier.toLowerCase() === tier.toLowerCase();
        });
      }
      return ranks;
    });
  }

  function getRank(name) {
    return getRanks().then(function(ranks) {
      var q = name.toLowerCase().replace(/\s+/g, ' ').trim();
      var found = ranks.filter(function(r) {
        return r.name.toLowerCase() === q ||
          r.file.replace(/\.png$/, '').toLowerCase() === q.replace(/[_\s]/g, '_');
      });
      return found[0] || null;
    });
  }

  function getAgent(name) {
    return getAgents().then(function(agents) {
      var found = agents.filter(function(a) {
        return a.name.toLowerCase() === name.toLowerCase();
      });
      return found[0] || null;
    });
  }

  function getWeapon(name) {
    return getWeapons().then(function(weapons) {
      var found = weapons.filter(function(w) {
        return w.name.toLowerCase() === name.toLowerCase();
      });
      return found[0] || null;
    });
  }

  function getMap(name) {
    return getMaps().then(function(maps) {
      var found = maps.filter(function(m) {
        return m.name.toLowerCase() === name.toLowerCase();
      });
      return found[0] || null;
    });
  }

  function search(query) {
    var q = query.toLowerCase();
    return Promise.all([getAgents(), getWeapons(), getMaps()]).then(function(results) {
      var agents = results[0].filter(function(a) { return a.name.toLowerCase().indexOf(q) !== -1; });
      var weapons = results[1].filter(function(w) { return w.name.toLowerCase().indexOf(q) !== -1; });
      var maps = results[2].filter(function(m) { return m.name.toLowerCase().indexOf(q) !== -1; });
      return { agents: agents, weapons: weapons, maps: maps };
    });
  }

  function getAgentsByRole(role) {
    return getAgents().then(function(agents) {
      return agents.filter(function(a) { return a.role === role; });
    });
  }

  function getWeaponsByCategory(category) {
    return getWeapons().then(function(weapons) {
      return weapons.filter(function(w) { return w.category === category; });
    });
  }

  function clearCache() {
    _cache = {};
  }

  function version() {
    return '1.0.0';
  }

  return {
    setBaseUrl: _setBaseUrl,
    getAgents: getAgents,
    getWeapons: getWeapons,
    getMaps: getMaps,
    getSkins: getSkins,
    getRanks: getRanks,
    getRank: getRank,
    getAgent: getAgent,
    getWeapon: getWeapon,
    getMap: getMap,
    search: search,
    getAgentsByRole: getAgentsByRole,
    getWeaponsByCategory: getWeaponsByCategory,
    clearCache: clearCache,
    version: version
  };
}));
