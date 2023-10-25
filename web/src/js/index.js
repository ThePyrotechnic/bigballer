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

let basicMat;

const loader = new GLTFLoader();
let viewportInitialized = false;
let scene;
let camera;
let controls;
let renderer;

const initThree = async () => {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 20000);
  scene.add(camera);

  renderer = new THREE.WebGLRenderer();
  renderer.setClearColor(0xFFFFFF);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth / 4, window.innerHeight / 4);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  document.body.appendChild(renderer.domElement);

  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileCubemapShader();
  const envScene = new DebugEnvironment();
  const generatedCubeRenderTarget = pmremGenerator.fromScene(envScene);

  scene.background = generatedCubeRenderTarget.texture;

  metalMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0.644, 0.003, 0.005),
    metalness: 1,
    roughness: 0,
    transmission: 0,
    opacity: 1,
    // thickness: 0.2,
    // ior: 1.301,
    envMap: generatedCubeRenderTarget.texture,
  });

  // basicMat = new THREE.MeshPhysicalMaterial({
  //   color: new THREE.Color(1, 1, 1),
  //   metalness: 0,
  //   roughness: 0,
  //   transmission: 1,
  //   opacity: 0,
  //   thickness: 1,
  //   ior: 2.333,
  //   envMap: generatedCubeRenderTarget.texture,
  // });

  // basicMat = new THREE.MeshPhysicalMaterial({
  //   color: new THREE.Color(0.793, 0.793, 0.664),
  //   metalness: 0,
  //   ior: 1.5,
  //   envMap: generatedCubeRenderTarget.texture,
  // });

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
const viewGltf = (url) => {
  loader.load(
    url,
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

      object.traverse((node) => {
        if (node.isMesh) {
          node.material = basicMat;
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

  renderer.setSize(width / 4, height / 4);
};

const formatBaller = (ballerId, ballerData) => {
  const ballerDiv = document.createElement("div");

  const header = document.createElement("h3");
  const headerText = `${ballerData["modifier"]} ${ballerData["name"]} of ${ballerData["appraisal"]} quality`;
  header.appendChild(document.createTextNode(headerText));
  ballerDiv.appendChild(header);

  const subHeader = document.createElement("span");
  subHeader.appendChild(document.createTextNode(ballerId));
  ballerDiv.appendChild(subHeader)

  const btnPreview = document.createElement("button");
  btnPreview.appendChild(document.createTextNode("View Baller"));
  btnPreview.addEventListener("click", () => { viewGltf(ballerData["export_path"]) });
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
