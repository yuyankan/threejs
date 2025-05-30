import * as THREE from 'three';
import { parts2read,initial_position } from 'part2read';


// --- 零件数据 ---

const PARTS_CONFIG_FILE = 'partsname2read.json';

// --- DOM 元素 ---
const infoContainers = document.getElementById('infoContainers');


// 默认零件颜色
const DEFAULT_PART_COLOR = 0x00ff00;
const partInfoElements = {};




/**
 * 创建多个零件
 * @param {THREE.Scene} scene - Three.js 场景对象
 * @param {string[]} partsRead - 零件名称数组
 * @param {number[]} initialPositions - 零件初始 X 坐标数组
 * @returns {THREE.Mesh[]} - 创建的零件网格数组
 */

//roll_name = ['roller_l', 'roller_f','roller_f']
//roll_positon = [0, 4,6]

// --- 加载初始零件名称 ---
export async function loadInitialParts() {
    try {
        const response = await fetch(PARTS_CONFIG_FILE);
        const data = await response.json();
        return data.parts2read || [];
    } catch (error) {
        console.error('Error loading initial parts config:', error);
        return [];
    }
}


//create part info: div, name, 
// --- 创建零件信息 DOM 元素 ---
function createPartInfoElement(partName) {
    const infoDiv = document.createElement('div');//new var in fun
    infoDiv.id = `part-info-${partName.replace(/\s+/g, '-')}`;
    infoDiv.className = 'part-info hidden';
    infoDiv.classList.add('hidden')
    infoContainers.appendChild(infoDiv);
    partInfoElements[partName] = infoDiv; //change global varaint in place, if not create new variant within fun, withing let/const 
}

const initial_cyclinder = {
    'base_r':0.8,
    'base_h':1.5,
    //'base_c':0x00008b,
    'top_r':0.4,
    'top_h':1,
    //'top_c':0x00008b,
    'part_rota_x':7.8,
    'part_rota_y':1.2,

};

function part_rollers(){
    // 创建第一个圆柱壳
    const cylinderGeometry1 = new THREE.CylinderGeometry(initial_cyclinder['base_r'], initial_cyclinder['base_r'], initial_cyclinder['base_h'], 32, 1, false); // openEnded: true
    const material1 = new THREE.MeshStandardMaterial({ color: parts2read['roller_d'], roughness: 0.3, metalness: 0.2 , opacity:1}); // 红色，标准材质
    const cylinder1 = new THREE.Mesh(cylinderGeometry1, material1);
    //cylinder1.position.x = initialPositions_x[i];
    //cylinder1.position.y = initialPositions_y[i];
    //scene.add(cylinder1);


    // 创建第二个圆柱壳
    const cylinderGeometry2 = new THREE.CylinderGeometry(initial_cyclinder['top_r'], initial_cyclinder['top_r'], initial_cyclinder['top_h'], 32, 1, false); // openEnded: true
    const material2 = new THREE.MeshStandardMaterial({ color: parts2read['roller_d'], roughness: 0.5, metalness: 0.2 }); // 绿色，标准材质
    const cylinder2 = new THREE.Mesh(cylinderGeometry2, material2);
    cylinder2.position.y = cylinder1.position.y + initial_cyclinder['base_h']/2; // 放置在第一个圆柱壳顶部
    cylinder2.position.x = cylinder1.position.x + 0.2
    //scene.add(cylinder2);

    //create a group
    const part = new THREE.Group();
    part.add(cylinder1);
    part.add(cylinder2);
    //part.position.set(0,0,0)
    part.rotation.x = initial_cyclinder['part_rota_x'];
    part.rotation.y = initial_cyclinder['part_rota_y'];
    return part;

}


const initial_hoven = {
    'l':2,
    'h':0.8,
    'w':1.5,
    //'c':0x00ffff,
    'position_gap':0.2,
    'rota_x':0,
    'rota_y':-0.1,
}

function part_hoven(num1=2, r1=initial_hoven['l'], num2=0, r2=0){
    // 创建第一个圆柱壳
    const geometry1 = new THREE.BoxGeometry(r1, initial_hoven['h'], initial_hoven['w']);  // 宽度 = 2，高度 = 3，深度 = 4
    const material1 = new THREE.MeshStandardMaterial({ color: parts2read['hoven_suil'], opacity: 1, transparent: true} ); // 灰色
    const cuboid1 = new THREE.Mesh(geometry1, material1);
    //create a group
    const part = new THREE.Group();
    part.add(cuboid1);
    let last_positon_x = cuboid1.position.x

    for (let i = 1; i < num1; i++) {
        const cuboid_temp = cuboid1.clone();

        cuboid_temp.position.x = last_positon_x + r1 +initial_hoven['position_gap']; // 放置在第一个圆柱壳顶部
        last_positon_x = cuboid_temp.position.x
        part.add(cuboid_temp);
    }
    if (num2>0){
        const geometry1 = new THREE.BoxGeometry(r2, initial_hoven['h'], initial_hoven['w']);  // 宽度 = 2，高度 = 3，深度 = 4
        const material1 = new THREE.MeshStandardMaterial({ color: parts2read['hoven_suil'] ,opacity: 1, transparent: true}); // 灰色
        const cuboid11 = new THREE.Mesh(geometry1, material1);
        cuboid11.position.x = last_positon_x + r1 ;
        last_positon_x = cuboid11.position.x 
        part.add(cuboid11)
        
        for (let i = 1; i < num2; i++) {
            const cuboid_temp = cuboid11.clone();
    
            cuboid_temp.position.x = last_positon_x + r2 +initial_hoven['position_gap']; // 放置在第一个圆柱壳顶部
            last_positon_x = cuboid_temp.position.x
            part.add(cuboid_temp);
        }

    };
    
   
    //part.position.set(0,0,0)
    part.rotation.x = initial_hoven['rota_x'];
    part.rotation.y = initial_hoven['rota_y'];
    return part;

}



const initial_roll_glue = {
    'base_r':0.5,
    'base_h':1.5,
    //'base_c':0x1155ccff,
    'part_rota_x':7.8,
    'part_rota_y':1.2,
    'gap':0.3

};
function part_roll_glue(){
    // 创建第一个圆柱壳
    const cylinderGeometry1 = new THREE.CylinderGeometry(initial_roll_glue['base_r'], initial_roll_glue['base_r'], initial_roll_glue['base_h'], 32, 1, false); // openEnded: true
    const material1 = new THREE.MeshStandardMaterial({ color: parts2read['0x1155ccff'], roughness: 0.5, metalness: 0.2 }); // 红色，标准材质
    const cylinder1 = new THREE.Mesh(cylinderGeometry1, material1);
    cylinder1.rotation.x = Math.PI / 2;
    //cylinder1.position.x = initialPositions_x[i];
    //cylinder1.position.y = initialPositions_y[i];
    //scene.add(cylinder1);
    const cylinder2 = cylinder1.clone()
    cylinder2.position.y = cylinder1.position.y + initial_roll_glue['gap'] + 2*initial_roll_glue['base_r']; // 放置在第一个圆柱壳顶部
   
    //scene.add(cylinder2);

    //create a group
    const part = new THREE.Group();
    part.add(cylinder1);
    part.add(cylinder2);
    //part.position.set(0,0,0)
    //part.rotation.x = initial_cyclinder['part_rota_x'];
    //part.rotation.y = initial_cyclinder['part_rota_y'];
    return part;

}


const initial_roll_merge = {
    'base_r':0.6,
    'base_h':1.5,
    //'base_c':0x1155ccff,
    'top_r':0.3,
    'top_h':1.5,
    //'top_c':0x1155ccff,
    'part_rota_x':7.8,
    'part_rota_y':1.2,
    'gap':0.2

};

function part_roll_merge(){
    // 创建第一个圆柱壳
    const cylinderGeometry1 = new THREE.CylinderGeometry(initial_roll_merge['base_r'], initial_roll_merge['base_r'], initial_roll_merge['base_h'], 32, 1, false); // openEnded: true
    const material1 = new THREE.MeshStandardMaterial({ color: parts2read['roll_merge'], roughness: 0.5, metalness: 0.2 , opacity: 1, transparent: true }); // 红色，标准材质
    const cylinder1 = new THREE.Mesh(cylinderGeometry1, material1);
    cylinder1.rotation.x = Math.PI / 2;
    const cylinderGeometry2 = new THREE.CylinderGeometry(initial_roll_merge['top_r'], initial_roll_merge['top_r'], initial_roll_merge['top_h'], 32, 1, false); // openEnded: true
    const material2= new THREE.MeshStandardMaterial({ color: parts2read['roll_merge'], roughness: 0.5, metalness: 0.2 , opacity: 1, transparent: true }); // 红色，标准材质
    const cylinder2 = new THREE.Mesh(cylinderGeometry2, material2);
    cylinder2.rotation.x = Math.PI / 2;
    cylinder2.position.y = cylinder1.position.y + initial_roll_merge['gap'] + initial_roll_merge['base_r']+initial_roll_merge['top_r']; // 放置在第一个圆柱壳顶部
   
    //scene.add(cylinder2);

    //create a group
    const part = new THREE.Group();
    part.add(cylinder1);
    part.add(cylinder2);
    //part.position.set(0,0,0)
    //part.rotation.x = initial_cyclinder['part_rota_x'];
    //part.rotation.y = initial_cyclinder['part_rota_y'];
    return part;

}


const initial_guil = {
    'base_r':0.2,
    'base_h':1,
    //'base_c':0x1155ccff,
    'part_rota_x':Math.PI / 12,
    'part_rota_y':-Math.PI / 9,

};


    // 创建第一个圆柱壳
    
function part_roll_suil(){
    // 创建第一个圆柱壳
    const geometry1 = new THREE.CylinderGeometry(initial_guil['base_r'], initial_guil['base_r'], initial_guil['base_h'], 32, 1, false); // openEnded: true
    const material1 = new THREE.MeshStandardMaterial({ color: parts2read['roll_suil'], roughness: 0.5, metalness: 0.2 , opacity: 1, transparent: true }); // 红色，标准材质
    const cuboid1 = new THREE.Mesh(geometry1, material1);
    cuboid1.rotation.x = Math.PI / 2;
    const cuboid2 = cuboid1.clone();
    const cuboid3 = cuboid1.clone();
    const cuboid4 = cuboid1.clone();
    const cuboid5 = cuboid1.clone();
    const cuboid6 = cuboid1.clone();


 
    cuboid2.position.x = cuboid1.position.x - initial_guil['base_r'] * 2; // 放置在第一个圆柱壳顶部
    cuboid3.position.x = cuboid2.position.x - initial_guil['base_r'] * 2; // 放置在第一个圆柱壳顶部
    cuboid4.position.x = cuboid3.position.x - initial_guil['base_r'] * 1.5; // 放置在第一个圆柱壳顶部
    cuboid4.position.y = cuboid3.position.y + initial_guil['base_r'] * 1.5; // 放置在第一个圆柱壳顶部
    cuboid5.position.x = cuboid4.position.x
    cuboid5.position.y = cuboid4.position.y + initial_guil['base_r'] * 2;; // 放置在第一个圆柱壳顶部
    cuboid6.position.y = cuboid5.position.y + initial_guil['base_r'] * 2;; // 放置在第一个圆柱壳顶部
    cuboid6.position.x = cuboid5.position.x
    
   
    //scene.add(cylinder2);

    //create a group
    const part = new THREE.Group();
    part.add(cuboid1);
    part.add(cuboid2);
    part.add(cuboid3);
    part.add(cuboid4);
    part.add(cuboid5);
    part.add(cuboid6);

    //part.position.set(0,0,0)
    //part.rotation.x = initial_guil['part_rota_x'];
    //part.rotation.y = initial_guil['part_rota_y'];
    return part;

}


const initialPositions_x = [-6, -9, -7, -2, 0.5, 6.2, 3,8];
const initialPositions_y = [0, 0, 2, 0, 2,0, 0,0];
export async function createParts(scene,initialPartsList) {

    //const {shape, extrudeSettings} = common_roll()//common_roll();
    let parts = [];
    
    let partColors = []
  
    let myfun = [part_rollers(),
        part_roll_suil(),
        part_hoven(2, initial_hoven['l'], 0, 0),
        part_roll_glue(),
        part_hoven(2, initial_hoven['l'], 2, initial_hoven['l']/2), 
     
        part_roll_merge(),
        part_rollers(),
        part_rollers()]
    
  
  
    for (let i = 0; i < initialPartsList.length; i++) {
        const partName = initialPartsList[i];
        // 创建拉伸几何体
        //const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        //const material = new THREE.MeshStandardMaterial({ color: DEFAULT_PART_COLOR });
        //const part_3d = common_cyclinder();
        const part_3d = myfun[i];
        //part_3d.rotation.x = 0;
        //part_3d.rotation.y = 0;
        console.log(part_3d);
        // 设置倾斜角度 (例如绕 X 轴倾斜 30 度)
        //const angleInRadians_x = THREE.MathUtils.degToRad(angleInDegrees_x);
        //const angleInRadians_y = THREE.MathUtils.degToRad(angleInDegrees_y);
        //part_3d.rotation.x = angleInRadians_x;
        //part_3d.rotation.y = -angleInRadians_y;
        part_3d.position.x = initialPositions_x[i];
        part_3d.position.y = initialPositions_y[i];
        part_3d.userData = { name: partName };
        scene.add(part_3d);
        parts.push(part_3d);
        partColors.push('0x00ff00')
        createPartInfoElement(partName); // 在 parts.js 内部创建信息元素
    
    }
    console.log('test',parts);
    console.log('test2',partInfoElements);
    console.log('test3',partColors);

    return { parts: parts, partInfoElements: partInfoElements, partColors: partColors };;
}

export async function createParts_new(scene,initialPartsList) {

    //const {shape, extrudeSettings} = common_roll()//common_roll();
    let parts = [];
    
    let partColors = []
  
    for (let i = 0; i < initialPartsList.length; i++) {
        const partName = initialPartsList[i];
        // 创建拉伸几何体
        //const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        //const material = new THREE.MeshStandardMaterial({ color: DEFAULT_PART_COLOR });
        //const part_3d = common_cyclinder();
        const part_3d = part_roll_merge()
        console.log(part_3d)
        // 设置倾斜角度 (例如绕 X 轴倾斜 30 度)
        //const angleInRadians_x = THREE.MathUtils.degToRad(angleInDegrees_x);
        //const angleInRadians_y = THREE.MathUtils.degToRad(angleInDegrees_y);
        //part_3d.rotation.x = angleInRadians_x;
        //part_3d.rotation.y = -angleInRadians_y;
        console.log('ttt',initial_position[partName])
        part_3d.position.x = initial_position[partName][0];
        part_3d.position.y = initial_position[partName][1];
        part_3d.userData = { name: partName };
        scene.add(part_3d);
        parts.push(part_3d);
        partColors.push('0x00ff00')
        createPartInfoElement(partName); // 在 parts.js 内部创建信息元素
    
    }
    console.log('test',parts);
    return [parts,partInfoElements,partColors];
}





