await tools.browser_wait_for({time: 2});
var extractResult = await tools.browser_evaluate({script: 
  "try {" +
  "  var h = ['素材ID（巨量）','标题','星图任务ID','星图任务名称','抖音号昵称','抖音号','视频播放链接','下单账户名称','消耗','产品名称','数据统计日期'];" +
  "  var t = document.querySelectorAll('table'); var dt = t[1] || t[0];" +
  "  var rows = dt.querySelectorAll('tr'); var data = [];" +
  "  for (var i=0;i<rows.length;i++){" +
  "    var cells=rows[i].querySelectorAll('td,th'); if(cells.length<h.length) continue;" +
  "    var row={}; for(var j=0;j<h.length;j++){var c=cells[j]; var a=c.querySelector('a[href]'); row[h[j]]={text:c.textContent.trim(),link:a?a.href:''};}" +
  "    data.push(row);" +
  "  }" +
  "  var ap=document.querySelector('.arco-pagination-item-active');" +
  "  JSON.stringify({headers:h,currentPage:ap?ap.textContent.trim():'?',data:data,dataCount:data.length,success:true});" +
  "} catch(e){JSON.stringify({error:e.message});}"
});
text(extractResult);
var nextClick = await tools.browser_evaluate({script:
  "(function(){var nb=document.querySelector('.arco-pagination-item-next');if(nb&&nb.className.indexOf('disabled')===-1){nb.click();return'ok';}return'done';})()"
});
text('NEXT_CLICK_RESULT:' + nextClick);
await tools.browser_wait_for({time: 3});
text('PAGE_TURN_DONE');
