await tools.browser_wait_for({time: 2});
var snap = await tools.browser_snapshot({compact: true, maxDepth: 15, maxNodes: 500});
text(snap.content ? snap.content[0].text : JSON.stringify(snap));
