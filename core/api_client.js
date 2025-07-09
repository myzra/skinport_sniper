const { io } = require("socket.io-client");
const parser = require("socket.io-msgpack-parser");
const express = require("express");

const app = express();
let latestSales = [];
let seenItems = new Set();

const ITEM_EXPIRY_MS = 10000;
const CLEANUP_INTERVAL_MS = 2000;


// WebSocket connection
const socket = io("wss://skinport.com", {
  transports: ["websocket"],
  parser,
});

// Errorhandling
socket.on("connect_error", (err) => {
  console.error("Verbindungsfehler:", err);
});

function filterItems(sale, queryParams) {
    // if no filter params -> return all sales
    if (!queryParams.marketName && !queryParams.category && !queryParams.pattern && !queryParams.wear && !queryParams.exterior) {
        return true;
    }

    // match "marketName"
    if (queryParams.marketName) {
        const searchNames = queryParams.marketName.split(",").map(name => name.trim().toLowerCase());
        const matchesName = searchNames.some(name => sale.sale.marketName.toLowerCase().includes(name));
        if (!matchesName) return false;
    }

    // match "categroy"
    if (queryParams.category && sale.sale.category.toLowerCase() !== queryParams.category.toLowerCase()) {
        return false;
    }

    // match "pattern"
    if (queryParams.pattern) {
        const searchPatterns = queryParams.pattern.split(",").map(pat => parseInt(pat.trim(), 10));
        if (!searchPatterns.includes(sale.sale.pattern)) {
            return false;
        }
    }

    // match "wear"
    if (queryParams.wear && sale.sale.wear > parseFloat(queryParams.wear)) {
        return false;
    }

    // match "exterior"
    if (queryParams.exterior && sale.sale.exterior.toLowerCase() !== queryParams.exterior.toLowerCase()) {
        return false;
    }

    return true;
}

// Sale-Feed monitoring
socket.on("saleFeed", (data) => {
  const blacklist = ["Container", "Sticker", "Graffiti", "Agent", "Charm", "Key", "Patch", "Collectible", "Pass", "Music Kit"];
  
  if (data.eventType === "listed") {
    data.sales.forEach((sale) => {
      console.log("New Sale", sale.saleId, sale.marketName)
      const saleId = sale.saleId;
  
      if (!blacklist.includes(sale.category)) { // prefilter only weapons, gloves and knives
        if (!seenItems.has(saleId)) {
          seenItems.add(saleId);
          latestSales.push({
            eventType: data.eventType,
            sale,
            timestamp: Date.now()
          });
        }
      }
    });
    console.log("Filtered Live Sale Feed Data:", latestSales.length);
    console.log(latestSales[0]) // debug

  }
});

setInterval(() => {
  const now = Date.now();
 
  while (
    latestSales.length > 0 &&
    now - latestSales[0].timestamp > ITEM_EXPIRY_MS // remove after x seconds
  ) {
    const oldSale = latestSales.shift();
    seenItems.delete(oldSale.sale.saleId);
    console.log("Gelöschter Sale", oldSale.sale.saleId)
  }
}, CLEANUP_INTERVAL_MS);

// join sale-feed with needed params
socket.emit("saleFeedJoin", { currency: "EUR", locale: "en", appid: 730 });

// http route with dynamic filter 
app.get("/skinport-live", (req, res) => {
  const queryParams = req.query; // z. B. ?names=Karambit | Tiger Tooth,M9 Bayonet | Freehand
  const filteredSales = latestSales.filter((sale) => filterItems(sale, queryParams));
  res.json(filteredSales);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`HTTP Server läuft auf http://localhost:${PORT}`);
});

console.log("Verbunden mit Skinport WebSocket!");
