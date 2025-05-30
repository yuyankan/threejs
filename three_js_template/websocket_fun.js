// websocket_module.js

/**
 * 定义断线重连策略的函数。
 *
 * @param {number} attempts 当前重连尝试次数。
 * @param {number} initialInterval 初始重连间隔（毫秒）。
 * @param {number} maxAttempts 最大重连尝试次数。
 * @param {number} maxInterval 最大重连间隔（毫秒）。
 * @returns {number|null} 下一次尝试连接的延迟时间（毫秒），如果返回 null 则停止重连。
 */
function reconnectionStrategy(attempts, initialInterval = 1000, maxAttempts = 5, maxInterval = 10000) {
    if (attempts >= maxAttempts) {
        console.log(`已达到最大重连尝试次数 (${maxAttempts})，停止重连。`);
        return null;
    }
    const nextInterval = Math.min(initialInterval * Math.pow(2, attempts), maxInterval);
    console.log(`第 ${attempts + 1} 次尝试重连，间隔 ${nextInterval} 毫秒。`);
    return nextInterval;
}

/**
 * 初始化 WebSocket 连接，包含断线重连策略。
 *
 * @param {string} SERVER_URL WebSocket 服务器地址。
 * @param {function} onMessageHandler 处理接收到消息的回调函数，接收 event 对象。
 * @param {function} [onOpenHandler] 连接成功的回调函数，接收 WebSocket 实例。
 * @param {function} [onCloseHandler] 连接关闭的回调函数。
 * @param {function} [onErrorHandler] 连接发生错误的回调函数，接收 error 对象。
 * @param {function} [reconnectStrategyFn=reconnectionStrategy] 断线重连策略函数。
 * @returns {object} 包含 close 方法的 WebSocket 控制对象。
 */
export function initializeWebSocketWithReconnect(
    SERVER_URL,
    onMessageHandler,
    onOpenHandler,
    onCloseHandler,
    onErrorHandler,
    reconnectStrategyFn = reconnectionStrategy // 使用默认的重连策略
) {
    let ws = null;
    let reconnectAttempts = 0;
    let currentReconnectInterval = 0;
    let reconnectTimeoutId = null;

    function connect() {
        ws = new WebSocket(SERVER_URL);

        ws.onopen = () => {
            console.log("WebSocket 连接已建立");
            reconnectAttempts = 0;
            currentReconnectInterval = 0;
            clearTimeout(reconnectTimeoutId); // 清除可能的重连定时器
            if (onOpenHandler) {
                onOpenHandler(ws);
            }
        };

        ws.onmessage = async (event) => {
            console.log('11',onMessageHandler)
            console.log("接收到 WebSocket 数据:");
            if (onMessageHandler) {
                await onMessageHandler(event);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket 连接已关闭，尝试重新连接...");
            reconnect();
            if (onCloseHandler) {
                onCloseHandler();
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket 发生错误:", error);
            reconnect();
            if (onErrorHandler) {
                onErrorHandler(error);
            }
        };
    }

    function reconnect() {
        console.log('reconnect')
        const nextDelay = reconnectStrategyFn(reconnectAttempts);
        if (nextDelay !== null) {
            reconnectAttempts++;
            currentReconnectInterval = nextDelay;
            reconnectTimeoutId = setTimeout(connect, currentReconnectInterval);
        } else {
            console.log("停止尝试重新连接 WebSocket。");
        }
    }

    connect();

    return {
        close: () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                console.log("手动关闭 WebSocket 连接");
                ws.close();
            } else if (reconnectTimeoutId) {
                clearTimeout(reconnectTimeoutId);
                console.log("手动停止 WebSocket 重连。");
            }
        }
    };
}

/**
 * 默认的 WebSocket 消息处理函数示例。
 * 你需要在你的主文件中实现你自己的消息处理逻辑。
 *
 * @param {MessageEvent} event WebSocket 消息事件对象。
 */
export async function defaultWebSocketMessageHandler(event) {
    console.log("默认 WebSocket 消息处理:", event.data);
    try {
        const parsedData = JSON.parse(event.data);
        console.log("解析后的数据:", parsedData);
        // 根据 parsedData 更新你的应用程序状态或 Three.js 场景
    } catch (error) {
        console.error("解析 WebSocket 数据失败:", error);
    }
}

/**
 * 默认的 WebSocket 连接成功处理函数示例。
 *
 * @param {WebSocket} ws WebSocket 实例。
 */
export function defaultWebSocketOpenHandler(ws) {
    console.log("WebSocket 连接成功。");
    // 可在此处发送初始化消息，例如：
    // ws.send(JSON.stringify({ type: 'initial_request' }));
}

/**
 * 默认的 WebSocket 连接关闭处理函数示例。
 */
export function defaultWebSocketCloseHandler() {
    console.log("WebSocket 连接已关闭。");
    // 可在此处添加重连逻辑或其他清理操作。
}

/**
 * 默认的 WebSocket 错误处理函数示例。
 *
 * @param {Event} error 错误事件对象。
 */
export function defaultWebSocketErrorHandler(error) {
    console.error("WebSocket 发生错误:", error);
    // 可在此处添加错误报告或重试逻辑。
}




