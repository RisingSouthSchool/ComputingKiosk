// Kiosk stats: the "This week at the kiosk" strip on the home screen, the stats
// dashboard it opens, and a detail page for each game / app / program / video.
// All numbers come from /api/stats (see server.py): counts of plays and minutes
// on this kiosk, nothing that identifies anyone. Runs after the main hub script
// and uses its globals (games, webapps, votes, view, openGame, showLanding ...).
(() => {
  const PERIODS = [["week", "This week"], ["term", "This term"], ["all", "All time"]];
  const KINDS = [["all", "All"], ["game", "Games"], ["webapp", "Web apps"], ["python", "Python"], ["db", "Databases"], ["video", "Videos"]];
  const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const FULL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const REFRESH_MS = 60000;

  const homeStats = document.getElementById("home-stats");
  const statsView = document.getElementById("stats-view");
  const root = document.getElementById("stats-root");
  const state = { period: "week", kind: "all", screen: "dashboard", item: null };
  let requestId = 0;

  // Small DOM helper: text always goes in as text, never as HTML.
  function h(tag, props = {}, ...kids) {
    const element = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
      if (value === false || value == null) continue;
      if (key === "class") element.className = value;
      else if (key === "text") element.textContent = value;
      else if (key === "style") element.style.cssText = value;
      else if (key.startsWith("on")) element.addEventListener(key.slice(2), value);
      else element.setAttribute(key, value === true ? "" : value);
    }
    for (const kid of kids.flat()) if (kid != null && kid !== false) element.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
    return element;
  }

  const fmtDuration = seconds => {
    if (!seconds) return "0s";
    if (seconds < 60) return seconds + "s";
    const minutes = Math.floor(seconds / 60), rest = seconds % 60;
    return minutes + "m " + String(rest).padStart(2, "0") + "s";
  };
  const hourLabel = hour => ((hour + 11) % 12 + 1) + (hour < 12 ? "am" : "pm");
  const shortDate = text => { const [, month, day] = text.split("-").map(Number); return day + " " + MONTHS[month - 1]; };
  const percent = (part, whole) => (whole ? Math.round(part / whole * 100) + "%" : "0%");

  function humanise(file) { return file.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim(); }

  // Name, tag and likes for an item, from the manifests the hub already loaded.
  function itemInfo(kind, slug) {
    if (kind === "game") {
      const game = games.find(item => item.slug === slug);
      return { title: game ? game.title : humanise(slug), tag: game ? gameTagText(game) : "Game", likes: votes[slug] ?? 0, playable: game || null };
    }
    if (kind === "webapp") {
      const app = webapps.find(item => item.slug === slug);
      return { title: app ? app.title : humanise(slug), tag: "Web app", likes: votes["webapp:" + slug] ?? 0, playable: app || null };
    }
    if (kind === "python") {
      const project = pythonProjects.find(item => item.slug === slug);
      return { title: project ? project.title : humanise(slug), tag: "Python", likes: null, playable: null };
    }
    if (kind === "db") {
      const project = dbProjects.find(item => item.slug === slug);
      return { title: project ? project.title : humanise(slug), tag: "Database", likes: null, playable: null };
    }
    if (slug.startsWith("microbit:")) return { title: humanise(slug.slice("microbit:".length)), tag: "Micro:bit video", likes: null, playable: null };
    return { title: humanise(slug), tag: "Escape-room video", likes: null, playable: null };
  }

  const getStats = (period, kind, slug) => {
    const query = new URLSearchParams({ period });
    if (kind && kind !== "all") query.set("kind", kind);
    if (slug) query.set("slug", slug);
    return fetch("/api/stats?" + query, { cache: "no-store" }).then(response => { if (!response.ok) throw new Error("stats"); return response.json(); });
  };

  // ---- shared pieces --------------------------------------------------

  // Mon-Fri heat grid over the school day, widened if anything happened outside it.
  function heatmap(data, cellHeight) {
    let low = 8, high = 15, busiest = { plays: 0 };
    data.heatmap.slice(0, 5).forEach((row, day) => row.forEach((plays, hour) => {
      if (plays) { low = Math.min(low, hour); high = Math.max(high, hour); }
      if (plays > busiest.plays) busiest = { plays, day, hour };
    }));
    const hours = Array.from({ length: high - low + 1 }, (_, index) => low + index);
    const max = Math.max(1, busiest.plays);
    const grid = h("div", { class: "st-heat", style: `grid-template-columns: 38px repeat(${hours.length}, minmax(0, 1fr))`, role: "img", "aria-label": "Plays by weekday and hour" },
      h("span"), hours.map(hour => h("span", { class: "st-hl", text: ((hour + 11) % 12 + 1) })));
    DAYS.forEach((name, day) => {
      grid.append(h("span", { class: "st-dl", text: name }));
      hours.forEach(hour => {
        const plays = data.heatmap[day][hour];
        const alpha = plays ? (0.2 + plays / max * 0.8).toFixed(2) : 0;
        grid.append(h("div", { class: "st-cell", style: `height: ${cellHeight}px; ${plays ? `background: rgba(82, 214, 181, ${alpha})` : ""}`, title: `${FULL_DAYS[day]} ${hourLabel(hour)}: ${plays} ${plays === 1 ? "play" : "plays"}` }));
      });
    });
    const label = busiest.plays ? `${FULL_DAYS[busiest.day]} ${hourLabel(busiest.hour)}` : null;
    return { grid, label, busiest };
  }

  function barRow(entry, max) {
    const info = itemInfo(entry.kind, entry.slug);
    return h("div", { class: "st-bar-row" },
      h("span", { class: "st-bar-name", text: info.title }),
      h("div", { class: "st-track" }, h("div", { class: "st-fill", style: `width: ${Math.round(entry.plays / max * 100)}%` })),
      h("span", { class: "st-num", text: entry.plays }));
  }

  const kpi = (label, value, note) => h("div", { class: "st-kpi" },
    h("span", { class: "st-kicker", text: label }), h("span", { class: "st-value", text: value }), h("span", { class: "st-note", text: note }));

  const chip = (label, pressed, onclick, key) => h("button", { type: "button", class: "st-chip", "aria-pressed": String(pressed), "data-focus": key, onclick }, label);

  // ---- home-page strip ------------------------------------------------

  function renderHomeStrip(data) {
    const panel = h("div", { class: "st-panel" },
      h("div", { class: "st-head" },
        h("h2", { text: "This week at the kiosk" }), h("span", { class: "st-spacer" }),
        h("button", { type: "button", class: "st-btn", onclick: enterStats }, "See all stats →")));
    if (!data.total_plays) {
      panel.append(h("p", { class: "st-empty", text: "No plays yet this week. Open a game and it will show up here." }));
    } else {
      const top = data.items.slice(0, 5), max = top[0].plays;
      const heat = heatmap(data, 20);
      panel.append(h("div", { class: "st-strip" },
        h("div", {}, h("div", { class: "st-big", text: data.total_plays }), h("div", { class: "st-muted", text: "plays since Monday" }),
          h("p", { class: "st-muted", style: "margin: 12px 0 0; font-size: .9rem" }, "Average play ", h("b", { style: "color: var(--ink)", text: fmtDuration(data.avg_seconds) }))),
        h("div", { class: "st-bars" }, h("span", { class: "st-kicker", text: "Most played" }), top.map(entry => barRow(entry, max))),
        h("div", {}, h("span", { class: "st-kicker", text: "Busiest times" }), heat.grid,
          heat.label ? h("p", { class: "st-muted", style: "margin: 8px 0 0; font-size: .9rem" }, "Busiest: ", h("b", { style: "color: var(--ink)", text: heat.label })) : null)));
    }
    homeStats.replaceChildren(panel);
    homeStats.hidden = false;
  }

  function refreshHomeStats() {
    getStats("week").then(renderHomeStrip).catch(() => { homeStats.hidden = true; });
  }

  // ---- dashboard ------------------------------------------------------

  function renderDashboard(data, focusKey) {
    const heat = heatmap(data, 34);
    const topItem = data.items[0];
    const change = data.previous_plays == null ? data.label
      : data.previous_plays === 0 ? "nothing to compare with yet"
      : (data.total_plays >= data.previous_plays ? "up " : "down ") + Math.abs(Math.round((data.total_plays - data.previous_plays) / data.previous_plays * 100)) + "% on this time last week";
    const maxWeek = Math.max(1, ...data.weeks.map(week => week.plays));
    const max = topItem ? topItem.plays : 1;

    const rows = data.items.slice(0, 12).map(entry => {
      const info = itemInfo(entry.kind, entry.slug);
      return h("button", { type: "button", class: "st-row", "data-focus": "r:" + entry.kind + ":" + entry.slug, onclick: () => openDetail(entry.kind, entry.slug) },
        h("div", { style: "min-width: 0" }, h("span", { class: "st-name" }, info.title, h("small", { text: info.tag })),
          h("div", { class: "st-track" }, h("div", { class: "st-fill", style: `width: ${Math.round(entry.plays / max * 100)}%` }))),
        h("span", { class: "st-plays", text: entry.plays }), h("span", { class: "st-muted", text: fmtDuration(entry.avg_seconds) }),
        h("span", { class: "st-muted", text: info.likes == null ? "–" : info.likes }));
    });

    root.replaceChildren(h("div", { class: "st-wrap" },
      h("div", { class: "st-top" },
        h("button", { type: "button", class: "st-back", "data-focus": "back", onclick: statsBack }, "← Home"),
        h("h1", { text: "Kiosk stats" }), h("span", { class: "st-spacer" }),
        h("a", { class: "st-btn quiet", href: "/api/usage.csv?period=" + state.period, download: "" }, "Download CSV")),
      h("div", { class: "st-chips" }, h("span", { class: "st-kicker", text: "Period" }),
        PERIODS.map(([id, label]) => chip(label, state.period === id, () => { state.period = id; loadDashboard("p:" + id); }, "p:" + id)),
        h("span", { class: "st-gap" }), h("span", { class: "st-kicker", text: "Show" }),
        KINDS.map(([id, label]) => chip(label, state.kind === id, () => { state.kind = id; loadDashboard("k:" + id); }, "k:" + id))),
      h("div", { class: "st-kpis" },
        kpi("Plays", data.total_plays, change),
        kpi("Average play", fmtDuration(data.avg_seconds), "per play"),
        kpi("Busiest time", heat.label || "–", heat.busiest.plays ? heat.busiest.plays + " plays in that hour" : "no plays yet"),
        kpi("Most played", topItem ? itemInfo(topItem.kind, topItem.slug).title : "–", topItem ? topItem.plays + " plays" : "no plays yet")),
      !data.total_plays ? h("div", { class: "st-panel" }, h("p", { class: "st-empty", text: "No plays in this period yet." })) :
      h("div", { class: "st-cols" },
        h("div", { class: "st-panel" }, h("h2", { class: "st-h", text: "Most played" }), h("p", { class: "st-sub", text: "Tap a row for details" }),
          h("div", { class: "st-table" },
            h("div", { class: "st-cols-head" }, h("span", { text: "GAME / APP" }), h("span", { text: "PLAYS" }), h("span", { text: "AVG TIME" }), h("span", { text: "LIKES" })), rows)),
        h("div", { class: "st-stack" },
          h("div", { class: "st-panel" }, h("h2", { class: "st-h", text: "When is the kiosk busiest?" }), heat.grid,
            h("p", { class: "st-foot", style: "margin-top: 10px", text: "Darker means more plays." })),
          h("div", { class: "st-panel" }, h("h2", { class: "st-h", text: "Plays by week" }),
            h("div", { class: "st-columns" }, data.weeks.map(week => h("div", { class: "st-col", title: "Week of " + shortDate(week.start) + ": " + week.plays }, h("span", { class: "st-count", text: week.plays }),
              h("div", { class: "st-fill", style: `height: ${Math.round(week.plays / maxWeek * 112)}px` })))),
            h("div", { class: "st-axis" }, data.weeks.map(week => h("span", { text: shortDate(week.start) })))))),
      h("p", { class: "st-foot", text: "A play is 30 seconds or more, counted once per game per visit. Every number is a count of plays and minutes on this kiosk. Nothing identifies a student." })));
    restoreFocus(focusKey);
  }

  // ---- item detail ----------------------------------------------------

  function renderDetail(data, focusKey) {
    const { kind, slug } = state.item;
    const info = itemInfo(kind, slug);
    const maxDay = Math.max(1, ...data.days.map(day => day.plays));
    const maxLength = Math.max(1, ...data.lengths.map(length => length.count));
    root.replaceChildren(h("div", { class: "st-wrap" },
      h("div", { class: "st-top" },
        h("button", { type: "button", class: "st-back", "data-focus": "back", onclick: statsBack }, "← All stats"),
        h("span", { class: "st-spacer" }),
        info.playable ? h("button", { type: "button", class: "st-btn", onclick: () => openGame(info.playable) }, "Play now") : null),
      h("div", { class: "st-title-block" }, h("h1", { style: "margin: 0; font-size: clamp(2rem, 5vw, 3rem)", text: info.title }), h("span", { class: "st-tag", text: info.tag })),
      h("div", { class: "st-kpis" },
        kpi("Plays", data.total_plays, data.label),
        kpi("Average play", fmtDuration(data.avg_seconds), "per play"),
        kpi("Likes", info.likes == null ? "–" : info.likes, info.likes == null ? "not available here" : "all time"),
        kpi("Quick exits", percent(data.quick_exits, data.sessions), "left in under 30 seconds")),
      h("div", { class: "st-cols" },
        h("div", { class: "st-panel" }, h("h2", { class: "st-h", text: "Plays per day, last 4 weeks" }),
          h("div", { class: "st-columns", style: "gap: 4px" }, data.days.map(day => h("div", { class: "st-col", title: shortDate(day.date) + ": " + day.plays }, h("div", { class: "st-fill", style: `height: ${Math.round(day.plays / maxDay * 130)}px` })))),
          h("div", { class: "st-axis ends" }, h("span", { text: shortDate(data.days[0].date) }), h("span", { text: shortDate(data.days[data.days.length - 1].date) }))),
        h("div", { class: "st-panel" }, h("h2", { class: "st-h", text: "How long do people stay?" }),
          h("div", { class: "st-bars" }, data.lengths.map(length => h("div", { class: "st-bar-row", style: "grid-template-columns: 110px minmax(0, 1fr) 40px" },
            h("span", { class: "st-bar-name", text: length.label }), h("div", { class: "st-track" }, h("div", { class: "st-fill", style: `width: ${Math.round(length.count / maxLength * 100)}%; ${length.count ? "" : "min-width: 0"}` })),
            h("span", { class: "st-num", text: length.count })))),
          h("p", { class: "st-foot", style: "margin-top: 12px", text: "Quick exits can mean a game is confusing or slow to load." }))),
      h("p", { class: "st-foot", text: "Period: " + data.label + ". The length chart counts every visit, including quick exits." })));
    restoreFocus(focusKey);
  }

  // ---- navigation and loading ----------------------------------------

  function restoreFocus(key) {
    const target = (key && root.querySelector(`[data-focus="${CSS.escape(key)}"]`)) || root.querySelector('[data-focus="back"]');
    target?.focus({ preventScroll: true });
  }

  function load(focusKey) {
    const ticket = ++requestId;
    const detail = state.screen === "detail";
    getStats(state.period, detail ? state.item.kind : state.kind, detail ? state.item.slug : null).then(data => {
      if (ticket !== requestId || view !== "stats") return;
      (detail ? renderDetail : renderDashboard)(data, focusKey);
    }).catch(() => {
      if (ticket !== requestId || view !== "stats") return;
      root.replaceChildren(h("div", { class: "st-wrap" },
        h("button", { type: "button", class: "st-back", "data-focus": "back", onclick: statsBack }, "← Home"),
        h("p", { class: "st-empty", text: "Could not load the stats. Try again in a moment." })));
      restoreFocus("back");
    });
  }
  const loadDashboard = focusKey => { state.screen = "dashboard"; load(focusKey); };

  function openDetail(kind, slug) {
    state.screen = "detail";
    state.item = { kind, slug };
    root.scrollIntoView?.({ block: "start" });
    window.scrollTo(0, 0);
    load("back");
  }

  function enterStats() {
    view = "stats";
    state.screen = "dashboard";
    landingView.classList.remove("open");
    statsView.classList.add("open");
    window.scrollTo(0, 0);
    root.replaceChildren(h("div", { class: "st-wrap" }, h("p", { class: "st-empty", text: "Loading stats…" })));
    load("back");
  }

  // Back button, Escape and gamepad B: detail -> dashboard -> home.
  function statsBack() {
    if (state.screen === "detail") { state.screen = "dashboard"; window.scrollTo(0, 0); load("r:" + state.item.kind + ":" + state.item.slug); return; }
    showLanding();
  }

  setInterval(() => { if (view === "stats" && !player.classList.contains("open")) load(document.activeElement?.dataset?.focus); }, REFRESH_MS);

  window.refreshHomeStats = refreshHomeStats;
  window.enterStats = enterStats;
  window.statsBack = statsBack;
  window.hideStatsView = () => statsView.classList.remove("open");
})();
