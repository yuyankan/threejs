import * as THREE from 'three';
import { parts2read } from 'part2read';

let parts=[];
let partInfoElements;
let partColors;

//const infoContainers = document.getElementById('partInfo'); // 从HTML获取

// --- 配置 ---
//const SERVER_URL = 'http://localhost:8000/status';



export function setPartsCallback(newParts,newpartInfoElements,newpartColors) {
    parts = newParts;
    partInfoElements=newpartInfoElements;
    partColors = newpartColors

}

// --- 创建表格 HTML ---
function createTableHTML(data) {
    if (!data || data.length === 0) {
        return "<p>没有相关信息。</p>";
    }
    let html = '<table class="part-info-table">';
    html += '<thead><tr>';
    for (const key in data[0]) {
        html += `<th>${key}</th>`;
    }
    html += '</tr></thead><tbody>';
    data.forEach(item => {
        html += '<tr>';
        for (const key in item) {
            html += `<td>${item[key] === null ? '' : item[key]}</td>`;
        }
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}

function setgroupcolor(group, color,partName){

    //recover default color
    if(color!=="#ff0000"){
        color = parts2read[partName]
    }
   
    group.children.forEach(child => {
        if (child.material) {
          if (Array.isArray(child.material)) {
            child.material.forEach(material => {
              material.color.set(color);
            });
          } else {
            child.material.color.set(color);
          }
        }
      });
}

// --- 获取和设置零件信息 ---



export async function fetchPartsData(event) {
    //ws.onmessage = (event) => {
    try {console.log('test:', event.data)
       
        const data = JSON.parse(event.data);
        
        if (data && data.part_colors && data.parts_info) {
            let partsData;
            partColors = data.part_colors;
            partsData = data.parts_info;

            partColors.forEach((hexColor, i) => {
                if (parts[i]) {
                    //parts[i].material.color.set(hexColor);
                    
                    const partName = parts[i].userData.name;
                    setgroupcolor(parts[i], hexColor, partName)
                    const infoDiv = partInfoElements[partName];
                    if (infoDiv) {
                        const relevantInfo = partsData.filter(item => item.part === partName);
                        const tableHTML = createTableHTML(relevantInfo);
                        infoDiv.innerHTML = tableHTML;
                        //这是 classList 对象的一个方法，用于切换指定的 CSS 类名。
                        //如果 force 为 true，则强制添加类名。
                        //如果 force 为 false，则强制移除类名。
                        //如果省略 force 参数，则如果元素没有该类名，就添加它；如果元素已经有该类名，就移除它。
                        infoDiv.classList.toggle('hidden', hexColor !== '#ff0000');
                    }
                }
            });
        }
    } catch (err) {
        console.error("获取零件数据失败", err);
    }
    return [parts,partInfoElements,partColors];
}

//}





// --- 更新零件信息位置 ---
export function updatePartInfoPosition0(part, infoElement, camera) {
    const vector = new THREE.Vector3();
    part.getWorldPosition(vector);
    vector.project(camera);

    const x = (vector.x + 1) / 2 * window.innerWidth;
    const y = (1 - vector.y) / 2 * window.innerHeight;

    infoElement.style.left = `${x}px`;
    infoElement.style.top = `${y}px`;
}

export function updatePartInfoPosition1(part, infoDiv, camera) {
    if (!part || !infoDiv || !camera) {
        return;
    }

    const worldPosition = new THREE.Vector3();
    part.getWorldPosition(worldPosition);//获取零件在 3D 世界空间中的位置

    const screenPosition = worldPosition.clone();
    screenPosition.project(camera);//将 3D 世界坐标投影到相机的 2D 屏幕空间坐标系中。返回的 x 和 y 值范围是 -1 到 1。

    const x = (screenPosition.x * 0.5 + 0.5) * renderer.domElement.clientWidth;//将 Three.js 中标准化设备坐标（NDC）从 [-1, 1] 的范围映射到 [0, 1] 的范围。
    const y = (screenPosition.y * -0.5 + 0.5) * renderer.domElement.clientHeight;//将 Three.js 中标准化设备坐标（NDC）从 [-1, 1] 的范围映射到 [0, 1] 的范围。

    infoDiv.style.left = `${x}px`;
    infoDiv.style.top = `${y}px`;
}

export function updatePartInfoPosition(part, infoElement, camera, renderer) {
    if (!part || !infoElement || !camera || !renderer) {
        return;
    }

    const worldPosition = new THREE.Vector3();
    part.getWorldPosition(worldPosition);

    const screenPosition = worldPosition.clone();
    screenPosition.project(camera);

    const x = (screenPosition.x * 0.5 + 0.5) * renderer.domElement.clientWidth;
    const y = (screenPosition.y * -0.5 + 0.5) * renderer.domElement.clientHeight;

    // 添加偏移量以调整信息元素的位置 (根据你的需求调整)
    const offsetX = -infoElement.offsetWidth / 2; // 水平居中
    const offsetY = -infoElement.offsetHeight - 10; // 显示在上方，留出 10px 间距

    infoElement.style.left = `${x + offsetX}px`;
    infoElement.style.top = `${y + offsetY}px`;
}


// --- 更新零件信息位置 ---
export function updatePartInfoPosition7(part, infoElement, camera) {
    const vector = new THREE.Vector3();
    part.getWorldPosition(vector);
    vector.project(camera);

    const x = (vector.x + 1) / 2 * window.innerWidth;
    const y = (1 - vector.y) / 2 * window.innerHeight;

    infoElement.style.left = `${x}px`;
    infoElement.style.top = `${y}px`;
}
