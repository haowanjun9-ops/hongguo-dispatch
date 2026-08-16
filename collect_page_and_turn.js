async function main() {
  const EXTRACT = `try {
    var h = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期'];
    var t = document.querySelectorAll('table'); var dt = t[1] || t[0];
    var rows = dt.querySelectorAll('tr'); var data = [];
    for (var i=0;i<rows.length;i++){
      var cells=rows[i].querySelectorAll('td,th'); if(cells.length<h.length) continue;
      var row={}; for(var j=0;j<h.length;j++){var c=cells[j]; var a=c.querySelector('a[href]'); row[h[j]]={text:c.textContent.trim(),link:a?a.href:''};}
      data.push(row);
    }
    var ap=document.querySelector('.arco-pagination-item-active');
    JSON.stringify({headers:h,currentPage:ap?ap.textContent.trim():'?',data:data,dataCount:data.length,success:true});
  } catch(e){JSON.stringify({error:e.message});}`;

  const NEXT = `(function(){var nb=document.querySelector('.arco-pagination-item-next');if(nb&&nb.className.indexOf('disabled')===-1){nb.click();return'ok';}return'done';})()`;

  console.log('STEP1:等待2秒');
  await new Promise(r => setTimeout(r, 2000));

  console.log('STEP2:提取数据');
  // 这里无法直接调用browser_evaluate，需要通过CDP或Exec环境
  // 直接输出占位
  console.log('NEED_EXEC_ENV');
}
main().then(()=>console.log('DONE')).catch(e=>console.log('ERR:',e.message));
