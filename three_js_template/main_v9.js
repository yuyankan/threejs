import * as THREE from 'three';
import { OrbitControls } from 'OrbitControls';
import { parts2read } from 'part2read';
import { loadInitialParts,createParts } from 'parts_creation';
import { fetchPartsData, setPartsCallback,updatePartInfoPosition } from 'parts_manage';
import { initializeWebSocketWithReconnect, defaultWebSocketOpenHandler, defaultWebSocketCloseHandler, defaultWebSocketErrorHandler } from 'websocket_fun';




// --- 配置 ---
//const REFRESH_INTERVAL = 10000; // 10 秒刷新一次
globalThis.EXPLODED_DISTANCE_MULTIPLIER = 2;
globalThis.SERVER_URL = 'ws://localhost:8000/ws/data';

globalThis.parts=[];
globalThis.partInfoElements = {};
globalThis.partColors=[];

globalThis.initialPartsList;

globalThis.scene;
function setupScene() {
    const scene = new THREE.Scene();
    return scene;
}

globalThis.camera;
function setupCamera() {
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 10);
    return camera;
}

globalThis.renderer;
function setupRenderer() {
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor('#36454F');
    document.body.appendChild(renderer.domElement);
    return renderer;
}

// --- 控制器和灯光 ---
globalThis.controls;

function setupControls() {
    const controls = new OrbitControls(globalThis.camera, globalThis.renderer.domElement);
    // 启用阻尼，使平移和旋转更加平滑 (可选)
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    return controls;
}

globalThis.light;

function setupLights() {
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 2, 3);
    globalThis.scene.add(light);
    return light;
}

// 监听窗口大小变化，并更新相机和渲染器尺寸
function onWindowResize() {
    globalThis.camera.aspect = window.innerWidth / window.innerHeight;
    globalThis.camera.updateProjectionMatrix();
    globalThis.renderer.setSize(window.innerWidth, window.innerHeight);
}



// --- 爆炸/恢复 动画 ---
globalThis.exploded = false;

function setupExplodeListener() {
    window.addEventListener('click', () => {
        globalThis.exploded = !globalThis.exploded;
        updatePartExplosion(globalThis.parts, globalThis.initialPositions, globalThis.exploded, globalThis.EXPLODED_DISTANCE_MULTIPLIER);
    });
}

function updatePartExplosion() {
    for (let i = 0; i < parts.length; i++) {
        globalThis.parts[i].position.x = globalThis.exploded ? globalThis.initialPositions[i] * globalThis.multiplier : globalThis.initialPositions[i];
    }
}

// --- 射线投射和交互 ---
globalThis.raycaster = new THREE.Raycaster();
globalThis.pointer = new THREE.Vector2();
globalThis.intersectedPart = null;



function setupRaycaster() {
    globalThis.renderer.domElement.addEventListener('mousemove', (event) => {
        globalThis.pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
        globalThis.pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;

        globalThis.raycaster.setFromCamera(globalThis.pointer, globalThis.camera);

        const intersects = globalThis.raycaster.intersectObjects(globalThis.parts);

        if (intersects.length > 0) {
            const hoveredPart = intersects[0].object;
            const partName = hoveredPart.userData.name;

            // 鼠标悬浮时，如果存在信息元素，则显示
            if (globalThis.partInfoElements[partName]) {
                globalThis.partInfoElements[partName].classList.remove('hidden');
            }
            globalThis.intersectedPart = hoveredPart;
        } else {
            if (globalThis.intersectedPart) {
                const partName = globalThis.intersectedPart.userData.name;
                const partIndex = globalThis.parts.indexOf(globalThis.intersectedPart);

                // 鼠标移开时，如果颜色不是红色，并且存在信息元素，则隐藏
                if (globalThis.partColors[partIndex] !== '#ff0000' && globalThis.partInfoElements[partName]) {
                    globalThis.partInfoElements[partName].classList.add('hidden');
                }
                globalThis.intersectedPart = null;
            }
        }
    });
}



// --- 动画循环 ---
  
function animate() {

    requestAnimationFrame(() => animate()); // 使用箭头函数
    globalThis.renderer.render(globalThis.scene, globalThis.camera);
    globalThis.controls.update();
    console.log('********************', globalThis.parts)
    
    globalThis.parts.forEach(part => {
        const partName = part.userData.name;
        //updatePartInfoPosition(part, partInfoElements[partName], camera);
        console.log('ttttt', partName, globalThis.partInfoElements[partName])
        updatePartInfoPosition(part, globalThis.partInfoElements[partName], globalThis.camera, globalThis.renderer) 
    });
}


//update data
async function handleMyWebSocketMessage(event) {
    console.log("主文件中的 WebSocket 消息处理:");
    try {
        //update info in place 
        console.log("color1:",partColors)     
        const data = await fetchPartsData(event);
        globalThis.parts = data.parts;
        globalThis.partInfoElements = data.partInfoElements;
        globalThis.partColors = data.partColors;
        console.log("color:",globalThis.partColors)

        if (globalThis.parts && globalThis.partInfoElements.length > 0) {
            setPartsCallback(globalThis.parts, globalThis.partInfoElements, globalThis.partColors);
            console.log("WebSocket 数据更新完成。");
        } 
        else {
            console.warn("接收到的 WebSocket 数据中不包含有效的零件信息。");
        }
            
    } catch (error) {
        console.error("处理 WebSocket 消息时发生错误 (在主文件中处理):", error);
    }
   
}

// --- 初始设置 ---


async function initialSetup() {
    //let renderer, scene, camera, controls, light; // 声明变量在函数作用域内

    // 初始化 Three.js 核心组件
    globalThis.renderer = setupRenderer();
    globalThis.scene = setupScene();
    globalThis.camera = setupCamera();
    globalThis.controls = setupControls();
    globalThis.light = setupLights();

    window.addEventListener('resize', onWindowResize, false);

    // 加载零件名称列表
    //initialPartsList = Object.keys(parts2read);
    globalThis.initialPartsList= ["roller_d",
            "roller_silicone",
            "oven_silicone",
            "roller_glue",
            "oven_glue",
            "roller_merge",
            "roller_f",
            "roller_finish"]
    console.log("初始零件名称列表:", globalThis.initialPartsList); // 更清晰的日志信息

    if (globalThis.initialPartsList && globalThis.initialPartsList.length > 0) {
        //let parts, partInfoElements, partColors; // 声明变量在 if 块作用域内

        // 创建初始零件
        console.log('initialPartsList',globalThis.initialPartsList)
        const data = await createParts(globalThis.scene, globalThis.initialPartsList);
        globalThis.parts = data.parts;
        globalThis.partInfoElements = data.partInfoElements;
        globalThis.partColors = data.partColors;

        console.log('初始零件创建完成:', globalThis.parts, globalThis.partColors); // 更清晰的日志信息
        setPartsCallback(globalThis.parts, globalThis.partInfoElements, globalThis.partColors); // 使用 parts_management.js 中的 setParts

        // 设置交互和渲染循环
        setupRaycaster();
        animate();


        // 初始化 WebSocket 连接，传入自定义的处理函数
        initializeWebSocketWithReconnect(
            globalThis.SERVER_URL,
            handleMyWebSocketMessage, // 使用自定义的消息处理函数
            () => defaultWebSocketOpenHandler(null), // 可以使用默认的 open handler 或自定义
            defaultWebSocketCloseHandler,
            defaultWebSocketErrorHandler
        );

        // 设置定时刷新 (如果需要)
        // setInterval(fetchAndUpdateData, 5000);

    } else {
        console.warn("未加载到有效的初始零件名称列表。");
    }
}
// --- 初始化 ---
function initialize() {
    initialSetup();
}

initialize();

/*<script type="module" src="parts_creation.js"></script>
<script type="module" src="parts_manage.js"></script>
*/
