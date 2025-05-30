import * as THREE from 'three';


// --- 零件数据 ---
const initialPositions_x = [-6, -2, 1];
const initialPositions_y = [1, 1, 1];
const PARTS_CONFIG_FILE = 'partsname2read.json';

// --- DOM 元素 ---
const infoContainers = document.getElementById('infoContainers');


// 默认零件颜色
const DEFAULT_PART_COLOR = 0x00ff00;
const partInfoElements = {};


const roll_common = { 'x':-0.5,
    'y':-0.5,
    'width':1,
    'height':1,
    'radius':0.1,
    'extrud_depth':1,
    'angleInDegrees_x':30,
    'angleInDegrees_y':-20
}

function common_roll(x=roll_common['x'], y=roll_common['y'], width=roll_common['width'], height=roll_common['width'], radius=roll_common['width'], extrud_depth=roll_common['extrud_depth']){
// 创建一个全局的 shape
    const shape = new THREE.Shape();
    shape.moveTo(x + radius, y);
    shape.lineTo(x + width - radius, y);
    shape.quadraticCurveTo(x + width, y, x + width, y + radius);
    shape.lineTo(x + width, y + height - radius);
    shape.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    shape.lineTo(x + radius, y + height);
    shape.quadraticCurveTo(x, y + height, x, y + height - radius);
    shape.lineTo(x, y + radius);
    shape.quadraticCurveTo(x, y, x + radius, y);

    // 拉伸的参数
    const extrudeSettings = {
        depth: extrud_depth,
        bevelEnabled: true,
        bevelSegments: 2,
        steps: 2,
        bevelSize: 0.1,
        bevelThickness: 0.1
    };
    return {shape, extrudeSettings}
}



function common_cylinder_shape(x=roll_common['x'], y=roll_common['y'], width=roll_common['width'], height=roll_common['width'], radius=roll_common['width'], extrud_depth=roll_common['extrud_depth']){
    // 创建一个全局的 shape
    // 1. 创建底部的 Shape
    const baseShape = new THREE.Shape();
    baseShape.ellipse(0, 0, 3, 5, 0, Math.PI * 2); // 底部椭圆

    // 2. 创建顶部的 Shape
    const topShape = new THREE.Shape();
    topShape.ellipse(0, 5, 0.5, 1, 0, Math.PI * 2); // 顶部椭圆，并向上移动了

    // 3. 定义挤压参数
    const extrudeSettings = {
        steps: 10,  // 更多的步数以获得更平滑的曲面
        depth: 1,
        bevelEnabled: false, //  不启用斜角
        //bevelThickness: 0.2,
        //bevelSize: 0.1,
        //bevelSegments: 5
    };

       // 4. 创建一个包含两个 Shape 的路径
       const shapes = [baseShape, topShape];  // 将底部的shape放在数组前面
        return {shapes, extrudeSettings}
    }




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

export function createParts(scene,initialPartsList,angleInDegrees_x=roll_common['angleInDegrees_x'], angleInDegrees_y=roll_common['angleInDegrees_y']) {

    const {shape, extrudeSettings} = common_roll()//common_roll();
    let parts = [];
    
    let partColors = []
  
    for (let i = 0; i < initialPartsList.length; i++) {
        const partName = initialPartsList[i];
        // 创建拉伸几何体
        const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        const material = new THREE.MeshStandardMaterial({ color: DEFAULT_PART_COLOR });
        const part_3d = new THREE.Mesh(geometry, material);
        // 设置倾斜角度 (例如绕 X 轴倾斜 30 度)
        const angleInRadians_x = THREE.MathUtils.degToRad(angleInDegrees_x);
        const angleInRadians_y = THREE.MathUtils.degToRad(angleInDegrees_y);
        part_3d.rotation.x = angleInRadians_x;
        part_3d.rotation.y = -angleInRadians_y;
        part_3d.position.x = initialPositions_x[i];
        part_3d.position.y = initialPositions_y[i];
        part_3d.userData = { name: partName };
        scene.add(part_3d);
        parts.push(part_3d);
        partColors.push('0x00ff00')
        createPartInfoElement(partName); // 在 parts.js 内部创建信息元素
    
    }
    //console.log('test',parts);
    return [parts,partInfoElements,partColors];
}


//create part info: div, name, 
// --- 创建零件信息 DOM 元素 ---
function createPartInfoElement(partName) {
    const infoDiv = document.createElement('div');//new var in fun
    infoDiv.id = `part-info-${partName.replace(/\s+/g, '-')}`;
    infoDiv.className = 'part-info hidden';
    infoContainers.appendChild(infoDiv);
    partInfoElements[partName] = infoDiv; //change global varaint in place, if not create new variant within fun, withing let/const 
}


function common_cyclinder(){
    // 创建第一个圆柱壳
    const cylinderGeometry1 = new THREE.CylinderGeometry(3, 5, 1, 32, 1, true); // openEnded: true
    const material1 = new THREE.MeshStandardMaterial({ color: 0x990000, roughness: 0.5, metalness: 0.2 }); // 红色，标准材质
    const cylinder1 = new THREE.Mesh(cylinderGeometry1, material1);
    cylinder1.position.x = initialPositions_x[i];
    cylinder1.position.y = initialPositions_y[i];
    scene.add(cylinder1);


    // 创建第二个圆柱壳
    const cylinderGeometry2 = new THREE.CylinderGeometry(0.5, 1, 2, 32, 1, true); // openEnded: true
    const material2 = new THREE.MeshStandardMaterial({ color: 0x009900, roughness: 0.5, metalness: 0.2 }); // 绿色，标准材质
    const cylinder2 = new THREE.Mesh(cylinderGeometry2, material2);
    cylinder2.position.y = cylinder1.position.y + 1; // 放置在第一个圆柱壳顶部
    scene.add(cylinder2);

}


