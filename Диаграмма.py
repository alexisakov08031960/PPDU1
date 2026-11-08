<mxfile host="app.diagrams.net">
  <diagram id="crypto-tkinter" name="Курсы криптовалют">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" pageWidth="1169" pageHeight="1654">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <mxCell id="t" value="Курсы криптовалют — Tkinter" style="text;html=1;fontSize=20;fontStyle=1;align=center;" vertex="1" parent="1">
          <mxGeometry x="60" y="20" width="900" height="40" as="geometry"/>
        </mxCell>

        <mxCell id="g" value="GUI-поток (root.mainloop)" style="swimlane;horizontal=0;startSize=34;fillColor=#EAF2FF;strokeColor=#7EA6E0;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="80" width="900" height="420" as="geometry"/>
        </mxCell>

        <mxCell id="init" value="Init: root = Tk()&lt;br&gt;coin_combobox.set('bitcoin')&lt;br&gt;quote_combobox.set('usd')" style="rounded=1;arcSize=6;fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;" vertex="1" parent="g">
          <mxGeometry x="30" y="50" width="270" height="70" as="geometry"/>
        </mxCell>
        <mxCell id="c1" value="Выбор криптовалюты&lt;br&gt;coin_combobox" style="rounded=1;arcSize=14;fillColor=#FFF2CC;strokeColor=#D6B656;align=left;spacingLeft=8;" vertex="1" parent="g">
          <mxGeometry x="30" y="150" width="270" height="55" as="geometry"/>
        </mxCell>
        <mxCell id="ev1" value="&lt;&lt;ComboboxSelected&gt;&gt;" style="shape=note;fillColor=#FFFFFF;strokeColor=#D6B656;size=12;fontSize=10;" vertex="1" parent="g">
          <mxGeometry x="340" y="155" width="150" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="u1" value="update_coin_label()" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;" vertex="1" parent="g">
          <mxGeometry x="530" y="155" width="180" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="c2" value="Выбор валюты котировки&lt;br&gt;quote_combobox" style="rounded=1;arcSize=14;fillColor=#FFF2CC;strokeColor=#D6B656;align=left;spacingLeft=8;" vertex="1" parent="g">
          <mxGeometry x="30" y="240" width="270" height="55" as="geometry"/>
        </mxCell>
        <mxCell id="ev2" value="&lt;&lt;ComboboxSelected&gt;&gt;" style="shape=note;fillColor=#FFFFFF;strokeColor=#D6B656;size=12;fontSize=10;" vertex="1" parent="g">
          <mxGeometry x="340" y="245" width="150" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="u2" value="update_quote_label()" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;" vertex="1" parent="g">
          <mxGeometry x="530" y="245" width="180" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="btn" value="Нажатие «Узнать курс»" style="rounded=1;arcSize=14;fillColor=#FFF2CC;strokeColor=#D6B656;" vertex="1" parent="g">
          <mxGeometry x="30" y="330" width="270" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="gr" value="get_crypto_rate()&lt;br&gt;Thread(target=fetch_price, daemon=True)" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;" vertex="1" parent="g">
          <mxGeometry x="340" y="325" width="370" height="60" as="geometry"/>
        </mxCell>

        <mxCell id="bg" value="Фоновый поток (daemon)" style="swimlane;horizontal=0;startSize=34;fillColor=#F5F5F5;strokeColor=#999999;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="520" width="900" height="560" as="geometry"/>
        </mxCell>

        <mxCell id="fp" value="fetch_price()" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;fontStyle=1;" vertex="1" parent="bg">
          <mxGeometry x="30" y="40" width="220" height="45" as="geometry"/>
        </mxCell>
        <mxCell id="rd" value="coin_id = coin_combobox.get()&lt;br&gt;quote = quote_combobox.get()" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="bg">
          <mxGeometry x="30" y="115" width="220" height="55" as="geometry"/>
        </mxCell>
        <mxCell id="d1" value="Выбраны&lt;br&gt;монета и валюта?" style="rhombus;fillColor=#D5E8D4;strokeColor=#82B366;fontSize=11;" vertex="1" parent="bg">
          <mxGeometry x="30" y="200" width="220" height="110" as="geometry"/>
        </mxCell>
        <mxCell id="warn" value="messagebox.showwarning&lt;br&gt;→ return" style="fillColor=#F8CECC;strokeColor=#B85450;dashed=1;fontSize=11;" vertex="1" parent="bg">
          <mxGeometry x="520" y="220" width="200" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="lock" value="button.config(state=DISABLED)&lt;br&gt;result_label = 'Запрос к API...'" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="bg">
          <mxGeometry x="30" y="345" width="230" height="55" as="geometry"/>
        </mxCell>
        <mxCell id="req" value="requests.get(API_URL, params, timeout=10)" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="bg">
          <mxGeometry x="30" y="440" width="230" height="50" as="geometry"/>
        </mxCell>

        <mxCell id="api" value="api.coingecko.com&lt;br&gt;/api/v3/simple/price" style="ellipse;shape=cloud;fillColor=#FCE7CD;strokeColor=#D79B00;" vertex="1" parent="1">
          <mxGeometry x="120" y="1120" width="280" height="100" as="geometry"/>
        </mxCell>

        <mxCell id="pr" value="Разбор ответа" style="swimlane;horizontal=0;startSize=34;fillColor=#E8F5E9;strokeColor=#82B366;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="1260" width="900" height="480" as="geometry"/>
        </mxCell>

        <mxCell id="d2" value="coin_id и quote&lt;br&gt;есть в data?" style="rhombus;fillColor=#D5E8D4;strokeColor=#82B366;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="30" y="40" width="220" height="110" as="geometry"/>
        </mxCell>
        <mxCell id="ek" value="showerror«Данные не найдены»&lt;br&gt;→ return" style="fillColor=#F8CECC;strokeColor=#B85450;dashed=1;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="480" y="65" width="220" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="ext" value="price = data[coin_id][quote]&lt;br&gt;change = ...24h_change" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="30" y="185" width="250" height="55" as="geometry"/>
        </mxCell>
        <mxCell id="fmt" value="format_price(price)" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="30" y="275" width="250" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="d3" value="change&lt;br&gt;не None?" style="rhombus;fillColor=#D5E8D4;strokeColor=#82B366;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="330" y="255" width="190" height="100" as="geometry"/>
        </mxCell>
        <mxCell id="arw" value="arrow = '▲' / '▼'&lt;br&gt;+ изменение в %" style="fillColor=#DDEBFF;strokeColor=#7EA6E0;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="570" y="270" width="230" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="sh" value="result_label.config(text=...)" style="rounded=1;arcSize=6;fillColor=#E1F5E1;strokeColor=#82B366;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="330" y="390" width="250" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="fin" value="finally: button.config(NORMAL)" style="fillColor=#E6E6E6;strokeColor=#666666;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="610" y="390" width="210" height="50" as="geometry"/>
        </mxCell>
        <mxCell id="ex" value="except Timeout / RequestException / Exception&lt;br&gt;showerror + result_label.config(text='')" style="rounded=1;arcSize=6;fillColor=#F8CECC;strokeColor=#B85450;dashed=1;align=left;spacingLeft=8;fontSize=11;" vertex="1" parent="pr">
          <mxGeometry x="480" y="150" width="390" height="70" as="geometry"/>
        </mxCell>

        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="init" target="c1"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="c1" target="ev1"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="ev1" target="u1"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="u1" target="c2"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="c2" target="ev2"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e6" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="ev2" target="u2"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="u2" target="btn"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e8" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="g" source="btn" target="gr"><mxGeometry relative="1" as="geometry"/></mxCell>

        <mxCell id="e9" value="new thread" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#1F3864;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="gr" target="fp"><mxGeometry relative="1" as="geometry"/></mxCell>

        <mxCell id="e10" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="bg" source="fp" target="rd"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e11" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="bg" source="rd" target="d1"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e12" value="Нет" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#B85450;fontSize=10;fontColor=#B85450;" edge="1" parent="bg" source="d1" target="warn"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e13" value="Да" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#82B366;fontSize=10;fontColor=#2D5016;" edge="1" parent="bg" source="d1" target="lock"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e14" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="bg" source="lock" target="req"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e15" value="HTTP GET" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#D79B00;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="req" target="api"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e16" value="JSON" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#D79B00;strokeWidth=2;fontSize=10;" edge="1" parent="1" source="api" target="d2"><mxGeometry relative="1" as="geometry"/></mxCell>

        <mxCell id="e17" value="Нет" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#B85450;fontSize=10;fontColor=#B85450;" edge="1" parent="pr" source="d2" target="ek"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e18" value="Да" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#82B366;fontSize=10;fontColor=#2D5016;" edge="1" parent="pr" source="d2" target="ext"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e19" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="pr" source="ext" target="fmt"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e20" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="pr" source="fmt" target="d3"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e21" value="Да" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#82B366;fontSize=10;fontColor=#2D5016;" edge="1" parent="pr" source="d3" target="arw"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e22" value="Нет" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;fontSize=10;" edge="1" parent="pr" source="d3" target="sh"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e23" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="pr" source="arw" target="sh"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e24" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;strokeColor=#666666;" edge="1" parent="pr" source="sh" target="fin"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e25" value="except" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;dashed=1;strokeColor=#B85450;fontSize=10;fontColor=#B85450;" edge="1" parent="1" source="req" target="ex"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e26" style="edgeStyle=orthogonalEdgeStyle;endArrow=block;dashed=1;strokeColor=#666666;" edge="1" parent="1" source="ex" target="fin"><mxGeometry relative="1" as="geometry"/></mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>