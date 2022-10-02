function getNodes(){
    eel.updateNodes()
}
eel.expose(addNodes);
function addNodes(nodes, len) {
  var cy = cytoscape({
    container: document.getElementById("cy"),
    elements: [
      // nodes
      { data: { id: "a" } },
      { data: { id: "b" } },
      { data: { id: "c" } },
      { data: { id: "d" } },
      { data: { id: "e" } },
      { data: { id: "f" } },
      // edges
      {
        data: {
          id: "ab",
          source: "a",
          target: "b",
        },
      },
      {
        data: {
          id: "cd",
          source: "c",
          target: "d",
        },
      },
      {
        data: {
          id: "ef",
          source: "e",
          target: "f",
        },
      },
      {
        data: {
          id: "ac",
          source: "a",
          target: "c",
        },
      },
      {
        data: {
          id: "be",
          source: "b",
          target: "e",
        },
      },
    ],
  });

  //用程式新增節點
  for (var i = 0; i < 10; i++) {
    cy.add({
      data: { id: "node" + i },
    });
    var source = "node" + i;
    cy.add({
      data: {
        id: "edge" + i,
        source: source,
        target: i % 2 == 0 ? "a" : "b",
      },
    });

    //重新排版
    cy.layout({
      name: "circle",
    }).run();
  }

  /*
  var cy = cytoscape({
    container: document.getElementById("cy"),
  });

  //用程式新增節點
  for (var i = 0; i < len; i++) {
    cy.add({
      data: { id: nodes[i].entity1.name },
      data: { id: nodes[i].entity2.name },
    });
    cy.add({
      data: {
        id: nodes[i].relation,
        source: nodes[i].entity1.name,
        target: nodes[i].entity2.name,
      },
    });
  }
  //重新排版
  cy.layout({
    name: "circle",
  }).run();*/
}

/*
var cy = cytoscape({
  container: document.getElementById("cy"),
  elements: [
    // nodes
    { data: { id: "a" } },
    { data: { id: "b" } },
    { data: { id: "c" } },
    { data: { id: "d" } },
    { data: { id: "e" } },
    { data: { id: "f" } },
    // edges
    {
      data: {
        id: "ab",
        source: "a",
        target: "b",
      },
    },
    {
      data: {
        id: "cd",
        source: "c",
        target: "d",
      },
    },
    {
      data: {
        id: "ef",
        source: "e",
        target: "f",
      },
    },
    {
      data: {
        id: "ac",
        source: "a",
        target: "c",
      },
    },
    {
      data: {
        id: "be",
        source: "b",
        target: "e",
      },
    },
  ],
});

//用程式新增節點
for (var i = 0; i < 10; i++) {
  cy.add({
    data: { id: "node" + i },
  });
  var source = "node" + i;
  cy.add({
    data: {
      id: "edge" + i,
      source: source,
      target: i % 2 == 0 ? "a" : "b",
    },
  });

  //重新排版
  cy.layout({
    name: "circle",
  }).run();
}
*/
