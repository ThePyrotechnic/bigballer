// bigballer web - collect items
//     Copyright (C) 2023  Michael Manis - michaelmanis@tutanota.com
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU Affero General Public License as published
//     by the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU Affero General Public License for more details.
//     You should have received a copy of the GNU Affero General Public License
//     along with this program.  If not, see <https://www.gnu.org/licenses/>.
import * as THREE from "three";

import { DebugEnvironment } from 'three/examples/jsm/environments/DebugEnvironment.js';
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
// import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

const accessToken = document.cookie.split("; ")
  .find((row) => row.startsWith("access_token="))?.split("=")[1];

let mat;

const loader = new GLTFLoader();
let viewportInitialized = false;
let scene;
let camera;
let controls;
let renderer;
let generatedCubeRenderTarget;

// adapted from:
// https://github.com/python/cpython/blob/3.11/Lib/colorsys.py
const hsvToRGB = (h, s, v) => {
  if (s == 0.0)
    return [v, v, v];

  let i = Math.floor(h * 6.0);
  const f = (h * 6.0) - i;
  const p = v * (1.0 - s);
  const q = v * (1.0 - s * f);
  const t = v * (1.0 - s * (1.0 - f));

  i = i % 6;
  if (i == 0)
    return [v, t, p];
  if (i == 1)
    return [q, v, p];
  if (i == 2)
    return [p, v, t];
  if (i == 3)
    return [p, q, v];
  if (i == 4)
    return [t, p, v];
  if (i == 5)
    return [v, p, q];
  // Cannot get here
}

const initThree = async () => {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 20000);
  scene.add(camera);

  renderer = new THREE.WebGLRenderer();
  renderer.setClearColor(0xFFFFFF);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  document.body.appendChild(renderer.domElement);

  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileCubemapShader();
  const envScene = new DebugEnvironment();
  generatedCubeRenderTarget = pmremGenerator.fromScene(envScene);

  scene.background = generatedCubeRenderTarget.texture;

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enablePan = false;

  const clock = new THREE.Clock(true);

  const animate = () => {
    requestAnimationFrame(animate);

    if (currentObject !== null) {
      // 1 rotation per second
      currentObject.rotation.y += 0.1047197 * clock.getDelta();
    }
    //controls.update(clock.getDelta());

    renderer.render(scene, camera);
  };
  animate();

  viewportInitialized = true;
};

// Thank you,
// https://github.com/donmccurdy/three-gltf-viewer
let currentObject = null;
const viewGltf = (ballerData) => {
  loader.load(
    ballerData["export_path"],
    (gltf) => {
      if (currentObject !== null) {
        scene.remove(currentObject);

        currentObject.traverse((node) => {
          if (node.isMesh) {
            node.geometry.dispose();
          }
        });
      }

      const object = gltf.scene;

      object.updateMatrixWorld();

      const box = new THREE.Box3().setFromObject(object);
      const size = box.getSize(new THREE.Vector3()).length();
      const center = box.getCenter(new THREE.Vector3());

      object.position.x += (object.position.x - center.x);
      object.position.y += (object.position.y - center.y);
      object.position.z += (object.position.z - center.z);

      let eyeIndex = 0;
      let itemIndex = 0;
      object.traverse((node) => {
        if (node.isMesh) {
          let curMaterial;
          if (node.name.startsWith("Eyes")) {
            let a = eyeIndex++ % ballerData["eye_materials"].length;
            curMaterial = ballerData["eye_materials"][a];
          }
          else if (node.name.startsWith("Items")) {
            let a = itemIndex++ % ballerData["item_materials"].length;
            curMaterial = ballerData["item_materials"][a];
          }
          else if (node.name.startsWith("Headwear")) {
            curMaterial = ballerData["headwear_material"]
          }
          else { // if (node.name == "Plain") { // Body node
            curMaterial = ballerData["body_material"];
          }

          let color = hsvToRGB(...curMaterial["color"]);
          let metalness = curMaterial["metalness"];
          let roughness = curMaterial["roughness"];
          let transmission = curMaterial["transmission"];
          let opacity = curMaterial["opacity"];
          let thickness = curMaterial["thickness"];
          let ior = curMaterial["ior"];

          node.material = new THREE.MeshPhysicalMaterial({
            color: new THREE.Color(...color),
            metalness: metalness,
            roughness: roughness,
            transmission: transmission,
            opacity: opacity,
            thickness: thickness,
            ior: ior,
            envMap: generatedCubeRenderTarget.texture,
          });
        }
      });

      camera.position.copy(center);
      camera.position.x += size / 2.0;
      camera.position.y += size / 5.0;
      camera.position.z += size / 2.0;
      camera.lookAt(center);

      controls.update();
      currentObject = object;
      scene.add(object);
    },
    (xhr) => {
      // console.log((xhr.loaded / xhr.total * 100) + "% loaded");
    },
    (error) => {
      throw error;
    }
  );
};

const onWindowResize = () => {
  const width = window.innerWidth;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width / 2, height / 2);
};

const formatBaller = (ballerId, ballerData) => {
  const ballerDiv = document.createElement("div");

  const header = document.createElement("h3");
  const headerText = ballerData["rarity_name"];
  header.appendChild(document.createTextNode(headerText));
  ballerDiv.appendChild(header);

  const subHeader = document.createElement("span");
  const height = (ballerData["height"] * 0.0328084).toFixed(3);
  const weight = (ballerData["weight"] * 0.002204623).toFixed(3);
  const roll = ballerData["roll"].toFixed(4);
  const materials = [ballerData["body_material"]["name"]];
  for (const mat of ballerData["eye_materials"])
    materials.push(mat["name"]);
  for (const mat of ballerData["item_materials"])
    materials.push(mat["name"]);
  if (ballerData["headwear_material"])
    materials.push(ballerData["headwear_material"]["name"]);
  subHeader.appendChild(document.createTextNode(`(${roll}) ${height} feet, ${weight} lbs. ${materials}`));
  ballerDiv.appendChild(subHeader)

  const btnPreview = document.createElement("button");
  btnPreview.appendChild(document.createTextNode("View Baller"));
  btnPreview.addEventListener("click", () => { viewGltf(ballerData) });
  ballerDiv.appendChild(btnPreview);

  return ballerDiv;
};

const getItems = async () => {
  const userId = document.getElementById("i-user-id-items").value;

  const res = await fetch("/api/items?" + new URLSearchParams({
    user_id: userId,
  }));
  const items = (await res.json()).items;

  document.getElementById("p-items-result").innerHTML = JSON.stringify(items);

  resultsElem = document.getElementById("p-items-result");
  resultsElem.textContent = "";
  for (const baller of items) {
    resultsElem.appendChild(formatBaller(baller["id"], baller));
  }
};

const getUsers = async () => {
  const searchKey = document.getElementById("i-user-search").value;

  const res = await fetch("/api/users?" + new URLSearchParams({
    like: searchKey,
  }));
  const users = (await res.json());

  document.getElementById("p-user-search-result").innerHTML = JSON.stringify(users);
};

const getMyTrades = async () => {
  const statusFilter = document.getElementById("select-trade-status").value;
  let url = "/api/trades"
  if (statusFilter !== "all") {
    url += "?" + new URLSearchParams({
      status: statusFilter,
    });
  }

  const res = await fetch(url);
  const trades = (await res.json());

  document.getElementById("p-trades-result").innerHTML = JSON.stringify(trades);
};

const getTrade = async () => {
  const tradeId = document.getElementById("i-trade-id").value;

  const res = await fetch(`/api/trade/${tradeId}`);
  const trades = (await res.json());

  document.getElementById("p-trade-details").innerHTML = JSON.stringify(trades);
};

const updateTrade = async () => {
  const tradeId = document.getElementById("i-trade-id").value;
  const newStatus = document.getElementById("select-update-trade-status").value;

  await fetch(`api/trade/${tradeId}`, {
    method: "POST",
    body: JSON.stringify({
      new_status: newStatus
    }),
    headers: { "Content-Type": "application/json" }
  });
};

const postTrade = async () => {
  const senderItems = document.getElementById("i-trade-own-items").value.split(",");
  const recipientId = document.getElementById("i-trade-recipient").value;
  const recipientItems = document.getElementById("i-trade-their-items").value.split(",");

  await fetch("/api/trade", {
    method: "POST",
    body: JSON.stringify({
      "sender_items": senderItems,
      "recipient_id": recipientId,
      "recipient_items": recipientItems
    }),
    headers: { "Content-Type": "application/json" }
  });
};

const postRoll = async (pack = false) => {
  const res = await fetch(
    "/api/roll" + "?" + new URLSearchParams(
      { pack: pack }
    ),
    { method: "POST" }
  );

  rollResultsElem = document.getElementById("p-roll-result");
  rollResultsElem.textContent = "";
  const rolls = await res.json();
  for (const [ballerId, ballerData] of Object.entries(rolls)) {
    rollResultsElem.appendChild(formatBaller(ballerId, ballerData));
  }

  postPinecones();
};

const postPinecones = async () => {
  if (!authenticated()) { return }

  const res = await fetch("/api/pinecones", { method: "POST" });
  const pinecones = await res.json();
  document.getElementById("p-pinecones").innerHTML = `${pinecones["total_pinecones"]} (+${pinecones["new_pinecones"]})`;
};

const authenticated = () => {
  return accessToken != null;
};

const login = () => {
  window.location = "/api/login";
};

const logout = () => {
  document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  window.location.reload();
};

document.addEventListener('DOMContentLoaded', async () => {
  if (document.cookie.match(/^(.*;)?\s*access_token\s*=\s*[^;]+(.*)?$/)) {
    document.getElementById("btn-login").setAttribute("disabled", "");

  } else {
    document.getElementById("btn-logout").setAttribute("disabled", "");
  }


  document.querySelector("#btn-login").addEventListener("click", login);
  document.querySelector("#btn-logout").addEventListener("click", logout);
  document.querySelector("#btn-roll").addEventListener("click", () => { postRoll() });
  document.querySelector("#btn-roll-group").addEventListener("click", () => { postRoll(true) });
  document.querySelector("#btn-user-search").addEventListener("click", getUsers);
  document.querySelector("#btn-items").addEventListener("click", getItems);
  document.querySelector("#btn-post-trade").addEventListener("click", postTrade);
  document.querySelector("#btn-my-trades").addEventListener("click", getMyTrades);
  document.querySelector("#btn-update-trade").addEventListener("click", updateTrade);
  document.querySelector("#btn-get-trade").addEventListener("click", getTrade);

  postPinecones();
  setInterval(postPinecones, 10000);

  await initThree();

  window.addEventListener("resize", onWindowResize);
});
