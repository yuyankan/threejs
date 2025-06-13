
/**
 * 当 Google Form 提交时触发此函数。
 * @param {Object} e 事件对象，包含表单响应信息。
 */
function onFormSubmit(e) {
  const formResponse = e.response;

      // 正确的做法：调用函数以获取实际的 ItemResponse 对象数组
  const itemResponses = formResponse.getItemResponses();

  Logger.log('--- 表单回复详情 ---');
  const re = {};


  itemResponses.forEach(itemResponse => {
    // 遍历每个 itemResponse 对象，然后访问其属性
    Logger.log(itemResponse.getItem());
  
    const questionTitle = itemResponse.getItem().getTitle(); // 获取问题标题
    const answer = itemResponse.getResponse(); // 获取用户提交的答案
    re[questionTitle] = answer;

    Logger.log(`${questionTitle}: ${answer}`);
    
  });

  const recipient = re['receiver'];
  const subject = re['subject'];
  const message_html = re['content'];

  //Logger.log('message_html (first 50 chars): ' + (message_html ? message_html.substring(0, 50) + "..." : "null"));
 


  // --- 2. 检查数据是否完整 ---
  if (!recipient || !subject || !message_html) {
    Logger.log('错误：邮件信息不完整。Recipient, Subject, or Message is missing.');
    // （可选）可以向表单所有者发送错误通知
    MailApp.sendEmail(Session.getEffectiveUser().getEmail(),
                      '表单邮件触发器 - 信息不完整',
                      '有一次表单提交，但邮件信息不完整。\n收件人: ' + recipient + '\n主题: ' + subject + '\n内容: ' + message_html +
                      '\n\n原始数据 (namedValues): ' + JSON.stringify(e.namedValues));
    return; // 退出函数，不发送邮件
  }

  // --- 3. 发送邮件 ---
  Logger.log('准备发送邮件至: ' + recipient);
  //MailApp.sendEmail(recipient, subject, message_html);
  GmailApp.sendEmail(recipient, subject, '', { // 注意：第三个参数是 plain body，这里留空
      htmlBody: message_html // 将你的 HTML 内容作为 htmlBody 选项传入
    });
  Logger.log('邮件已尝试发送至: ' + recipient + '，主题: ' + subject);

    // -
}
