# coding=utf-8
import os
import sys
import wx
import wx.html

class MyFrame(wx.Frame):
    def __init__(self):
        super(MyFrame,self).__init__(None,-1,u'记事本 - 无标题',size=(600,400))

        self.panel=wx.Panel(self,-1)
        self.text_edit=wx.TextCtrl(self.panel,style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_NOHIDESEL)
        self.text_edit.SetFont(wx.Font(11,wx.DEFAULT,wx.NORMAL,wx.NORMAL,faceName=u'宋体'))
        dt=MyFileDropTarget(self.text_edit)
        self.text_edit.SetDropTarget(dt)

        self.bsizer_h = wx.BoxSizer()
        self.bsizer_h.Add(self.text_edit,proportion=1,flag=wx.EXPAND|wx.ALL)
        self.panel.SetSizer(self.bsizer_h)

        self.app_name=u'记事本'
        self.current_file=''
        self.current_file_basename=''
        self.is_saved=True

        self.dlg_find=self.dlg_replace=None
        self.find_str=self.replace_str=''

        self.Centre()

        self.statusbar=wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-3,-1])
        self.statusbar.SetSize((-1,22))
        
        self.createMenus()
        self.addEvents()
        self.onTextChange(None)

    def createMenus(self):
        menubar=wx.MenuBar()

        # 文件
        file_menu=wx.Menu()
        self.file_menu_new=file_menu.Append(-1,u'新建(&N)\tCtrl+N')
        self.file_menu_open=file_menu.Append(-1,u'打开(&O)...\tCtrl+O')
        self.file_menu_save=file_menu.Append(-1,u'保存(&S)\tCtrl+S')
        self.file_menu_save_as=file_menu.Append(-1,u'另存为(&A)...')
        file_menu.AppendSeparator()
        self.file_menu_set=file_menu.Append(-1,u'页面设置(&U)...')
        self.file_menu_print=file_menu.Append(-1,u'打印(&P)...\tCtrl+P')
        file_menu.AppendSeparator()
        self.file_menu_exit=file_menu.Append(-1,u'退出(&X)')
        menubar.Append(file_menu,u'文件(&F)')
        
        # 编辑
        edit_menu=wx.Menu()
        self.edit_menu_undo=edit_menu.Append(-1,u'撤销(&U)\tCtrl+Z')
        self.edit_menu_cut=edit_menu.Append(-1,u'剪切(&T)\tCtrl+X')
        self.edit_menu_copy=edit_menu.Append(-1,u'复制(&C)\tCtrl+C')
        self.edit_menu_paste=edit_menu.Append(-1,u'粘贴(&P)\tCtrl+V')
        self.edit_menu_del=edit_menu.Append(-1,u'删除(&L)\tDel')
        edit_menu.AppendSeparator()
        self.edit_menu_find=edit_menu.Append(-1,u'查找(&F)...\tCtrl+F')
        self.edit_menu_find_next=edit_menu.Append(-1,u'查找下一个(&N)\tF3')
        self.edit_menu_replace=edit_menu.Append(-1,u'替换(&R)...\tCtrl+H')
        self.edit_menu_goto=edit_menu.Append(-1,u'转到(&G)...\tCtrl+G')
        edit_menu.AppendSeparator()
        self.edit_menu_select_all=edit_menu.Append(-1,u'全选(&A)\tCtrl+A')
        self.edit_menu_date=edit_menu.Append(-1,u'时间/日期(&D)\tF5')
        menubar.Append(edit_menu,u'编辑(&E)')

        # 格式
        format_menu=wx.Menu()
        self.format_menu_auto_wrap=format_menu.AppendCheckItem(-1,u'自动换行(&W)')
        self.format_menu_font=format_menu.Append(-1,u'字体(&F)...')
        menubar.Append(format_menu,u'格式(&O)')

        # 查看
        see_menu=wx.Menu()
        self.see_menu_statusbar=see_menu.AppendCheckItem(-1,u'状态栏(&S)')
        self.see_menu_statusbar.Check(True)
        menubar.Append(see_menu,u'查看(&V)')

        # 帮助
        help_menu=wx.Menu()
        self.help_menu_see=help_menu.Append(-1,u'查看帮助(&H)')
        self.help_menu_about=help_menu.Append(-1,u'关于记事本(&A)')
        menubar.Append(help_menu,u'帮助(&H)')

        self.SetMenuBar(menubar)

    def addEvents(self):
        # 文件子菜单
        self.Bind(wx.EVT_MENU,self.onNewFile,self.file_menu_new)
        self.Bind(wx.EVT_MENU,self.onOpenFile,self.file_menu_open)
        self.Bind(wx.EVT_MENU,self.onSaveFile,self.file_menu_save)
        self.Bind(wx.EVT_MENU,self.onSaveAsFile,self.file_menu_save_as)
        self.Bind(wx.EVT_MENU,self.onPageSet,self.file_menu_set)
        self.Bind(wx.EVT_MENU,self.onPrint,self.file_menu_print)
        self.Bind(wx.EVT_MENU,self.onExit,self.file_menu_exit)
        # 编辑子菜单
        self.Bind(wx.EVT_MENU,self.onUndo,self.edit_menu_undo)
        self.Bind(wx.EVT_MENU,self.onCut,self.edit_menu_cut)
        self.Bind(wx.EVT_MENU,self.onCopy,self.edit_menu_copy)
        self.Bind(wx.EVT_MENU,self.onPaste,self.edit_menu_paste)
        self.Bind(wx.EVT_MENU,self.onDelete,self.edit_menu_del)
        self.Bind(wx.EVT_MENU,self.onOpenFindDialog,self.edit_menu_find)
        self.Bind(wx.EVT_MENU,self.onFindNext,self.edit_menu_find_next)
        self.Bind(wx.EVT_MENU,self.onOpenReplaceDialog,self.edit_menu_replace)
        self.Bind(wx.EVT_MENU,self.onGoto,self.edit_menu_goto)
        self.Bind(wx.EVT_MENU,self.onSelectAll,self.edit_menu_select_all)
        self.Bind(wx.EVT_MENU,self.onInsertDate,self.edit_menu_date)
        # 格式子菜单
        self.Bind(wx.EVT_MENU,self.onAutoWrap,self.format_menu_auto_wrap)
        self.Bind(wx.EVT_MENU,self.onSetFont,self.format_menu_font)
        # 查看子菜单
        self.Bind(wx.EVT_MENU,self.onToggleStatusbar,self.see_menu_statusbar)
        # 帮助子菜单
        self.Bind(wx.EVT_MENU,self.onSeeHelp,self.help_menu_see)
        self.Bind(wx.EVT_MENU,self.onSeeAbout,self.help_menu_about)
        # 文本编辑框
        self.Bind(wx.EVT_TEXT,self.onTextChange,self.text_edit)
        # 空闲时候
        self.Bind(wx.EVT_IDLE,self.onIdle)
        # 窗口调整大小
        #self.Bind(wx.EVT_SIZE,self.onWindowResize)
        # 窗口查找和替换
        self.Bind(wx.EVT_FIND,self.onWindowFindNext)
        self.Bind(wx.EVT_FIND_NEXT,self.onWindowFindNext)
        self.Bind(wx.EVT_FIND_REPLACE,self.onWindowReplace)
        self.Bind(wx.EVT_FIND_REPLACE_ALL,self.onWindowReplaceAll)
        self.Bind(wx.EVT_FIND_CLOSE,self.onWindowFindClose)
        # 关闭程序
        self.Bind(wx.EVT_CLOSE,self.onWindowClose)

    def initEditor(self):
        self.text_edit.SetValue('')
        self.current_file=''
        self.current_file_basename=''
        self.SetTitle(u'无标题 - '+self.app_name)

    # 文件子菜单事件
    def onNewFile(self,event):
        if not (self.current_file or self.text_edit.GetValue()):
            return
        else:
            if not self.is_saved and self.text_edit.IsModified():
                filename=self.current_file.decode('utf-8') or u'无标题'
                dlg=wx.MessageDialog(None,u'是否将更改保存到 '+filename+' ?',u'记事本',wx.YES_NO|wx.CANCEL)
                val=dlg.ShowModal()
                if val==wx.ID_YES:
                    if not self.onSaveFile(None):
                        return
                elif val==wx.ID_CANCEL:
                    return
            self.initEditor()

    def onOpenFile(self,event):
        if not self.is_saved and self.text_edit.IsModified():
            filename=self.current_file_basename or u'无标题'
            dlg=wx.MessageDialog(self,u'是否将更改保存到 '+filename+' ?',u'记事本',wx.YES_NO|wx.CANCEL)
            val=dlg.ShowModal()
            if val==wx.ID_CANCEL:
                return False
            elif val==wx.ID_YES:
                if not self.onSaveFile(None):return
        dlg_open=wx.FileDialog(self,u'打开',unicode(os.getcwd(),sys.getfilesystemencoding()),'','',style=wx.ID_OPEN|wx.DD_CHANGE_DIR)
        if dlg_open.ShowModal()==wx.ID_OK:
            temp_file=unicode(dlg_open.GetPath()).encode('utf-8')
            if not os.path.exists(temp_file.decode('utf-8')):
                dlg_warning=wx.MessageDialog(None,u'文件未找到',u'记事本',wx.OK|wx.ICON_ERROR)
                dlg_warning.ShowModal()
                dlg_warning.Destroy()
                return False
            if self.text_edit.LoadFile(temp_file):
                self.current_file=temp_file
                self.current_file_basename=os.path.basename(self.current_file.decode('utf-8'))
                self.SetTitle(unicode(self.current_file_basename)+' - '+self.app_name)

    def onSaveFile(self,event):
        if not os.path.exists(self.current_file.decode('utf-8')):
            dlg=wx.FileDialog(self,u'保存文件',unicode(os.getcwd(),sys.getfilesystemencoding()),'',style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_CANCEL:return False
            self.current_file=unicode(dlg.GetPath()).encode('utf-8')
            self.current_file_basename=os.path.basename(unicode(self.current_file,'utf-8').encode('utf-8').decode('utf-8'))
        self.SetTitle(unicode(self.current_file_basename)+' - '+self.app_name)
        self.text_edit.SaveFile(self.current_file)
        self.is_saved=True
        return True

    def onSaveAsFile(self,event):
        dlg=wx.FileDialog(self,u'另存为',unicode(os.getcwd(),sys.getfilesystemencoding()),'',style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)
        if dlg.ShowModal()==wx.ID_OK:
            self.current_file=unicode(dlg.GetPath()).encode('utf-8')
            self.current_file_basename=os.path.basename(unicode(self.current_file,'utf-8').encode('utf-8').decode('utf-8'))
            self.SetTitle(unicode(self.current_file_basename)+' - '+self.app_name)
            self.text_edit.SaveFile(self.current_file)
            self.is_saved=True

    def onPageSet(self,event):
        pass

    def onPrint(self,event):
        pass

    def onExit(self,event):
        self.Close()

    # 编辑子菜单事件
    def onUndo(self,event):
        self.text_edit.Undo()

    def onCut(self,event):
        self.text_edit.Cut()

    def onCopy(self,event):
        self.text_edit.Copy()

    def onPaste(self,event):
        self.text_edit.Paste()

    def onDelete(self,event):
        self.text_edit.RemoveSelection()

    def onOpenFindDialog(self,event):
        self.text_content=self.text_edit.GetValue().replace('\n', '\r\n')
        if self.dlg_replace:
            self.dlg_replace.SetFocus()
            return
        if self.dlg_find:
            self.dlg_find.SetFocus()
        else:
            self.data=wx.FindReplaceData()
            self.dlg_find=wx.FindReplaceDialog(self,self.data,u' 查找')
            self.data.SetFindString(self.find_str)
            self.dlg_find.Show()

    def onFindNext(self,event):
        if self.find_str:
            self.onWindowFindNext(None)
        else:
            self.onOpenFindDialog(None)

    def onOpenReplaceDialog(self,event):
        self.text_content=self.text_edit.GetValue().replace('\n', '\r\n')
        if self.dlg_find:
            self.dlg_find.SetFocus()
            return
        if self.dlg_replace:
            self.dlg_replace.SetFocus()
        else:
            self.data=wx.FindReplaceData()
            self.dlg_replace=wx.FindReplaceDialog(self,self.data,u' 查找与替换',wx.ID_REPLACE)
            self.data.SetFindString(self.find_str)
            self.data.SetReplaceString(self.replace_str)
            self.dlg_replace.Show()

    # 窗体文本查找和替换
    def onWindowFindClose(self,event):
        event.EventObject.Destroy()

    def onWindowFindNext(self,event):
        
        # 首先获取查找字符串及其长度
        # 如果有选中字符串，那么
        # 获取选中字符串开始和结束位置
        # 开始点为 选中字符串行列坐标转化为索引 加上字符串长度
        # 查找子字符串

        # 否则
        # 开始点为 编辑区插入点
        # 查找子字符串

        # 如果未找到
        # 弹出提示信息模态框
        # 注销模态框
        # 函数返回
        
        # 如果找到子字符串
        # 那么在编辑区选中它

        self.find_str=self.data.GetFindString()
        fs_len=len(self.find_str)
        if self.text_edit.GetStringSelection():
            start,end=self.text_edit.GetSelection()
            start_point=self.text_edit.XYToPosition(start,end)+fs_len
            temp_pos=self.text_content.find(self.find_str,start_point+1)
        else:
            start_point=self.text_edit.GetInsertionPoint()
            temp_pos=self.text_content.find(self.find_str,start_point)
        if temp_pos==-1:
            dlg=wx.MessageDialog(self,u'查找已达到尾部！',u'提示',style=0)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.text_edit.SetSelection(temp_pos,temp_pos+fs_len)
        
    def onWindowReplace(self,event):

        # 取到查找和替换字符串以及选中字符串
        # 如果有选中字符串
        # 比较是否与查找字符串相等
        # 如果相等，获取选中字符串开始和结束位置，然后替换
        # 接着查找下一个

        self.find_str=self.data.GetFindString()
        self.replace_str=self.data.GetReplaceString()
        sel_text=self.text_edit.GetStringSelection()
        if sel_text:
            if sel_text==self.find_str:
                start,end=self.text_edit.GetSelection()
                self.text_edit.Replace(start,end,self.replace_str)
        self.onWindowFindNext(None)

    def onWindowReplaceAll(self,event):
        self.find_str=self.data.GetFindString()
        self.replace_str=self.data.GetReplaceString()
        self.text_edit.SetValue(self.text_content.replace(self.find_str,self.replace_str))

    # 跳转指定行
    def onGoto(self,event):
        cur_row=self.text_edit.PositionToXY(self.text_edit.GetInsertionPoint())[2]
        dlg=GotoDialog(self,self.text_edit.GetNumberOfLines(),cur_row)
        if dlg.ShowModal()==wx.ID_OK:
            row=int(dlg.FindWindowByName('spin').GetValue())
            pos=self.text_edit.XYToPosition(0,row-1)
            self.text_edit.ShowPosition(pos)
            self.text_edit.SetInsertionPoint(pos)
        dlg.Destroy()

    def onSelectAll(self,event):
        self.text_edit.SelectAll()

    def onInsertDate(self,event):
        self.text_edit.WriteText(wx.DateTime().Now().FormatISOCombined(' '))

    # 格式子菜单事件 切换自动换行
    def onAutoWrap(self,event):
        text=self.text_edit.GetValue()
        font=self.text_edit.GetFont()
        pos=self.text_edit.GetInsertionPoint()
        self.text_edit.Destroy()
        w_style=wx.TE_MULTILINE | wx.TE_DONTWRAP|wx.TE_NOHIDESEL
        if self.format_menu_auto_wrap.IsChecked():
            w_style=wx.TE_MULTILINE|wx.TE_WORDWRAP|wx.TE_NOHIDESEL
        self.text_edit=wx.TextCtrl(self.panel,-1,style=w_style)
        self.text_edit.SetFont(font)
        self.bsizer_h.Add(self.text_edit,proportion=1,flag=wx.EXPAND|wx.ALL)
        self.text_edit.SetSize(self.panel.Size)
        self.text_edit.SetValue(text)
        self.text_edit.SetFocus()
        self.text_edit.ShowPosition(pos)
        self.text_edit.SetInsertionPoint(pos)
        dt=MyFileDropTarget(self.text_edit)
        self.text_edit.SetDropTarget(dt)

    def onSetFont(self,event):
        font=wx.GetFontFromUser(self,self.text_edit.GetFont())
        if font.IsOk():
            self.text_edit.SetFont(font)

    # 查看子菜单事件 切换状态栏显示与隐藏
    def onToggleStatusbar(self,event):
        if self.see_menu_statusbar.IsChecked():
            self.statusbar.Show()
        else:
            self.statusbar.Hide()
        self.panel.SetSize(self.ClientSize)

    # 帮助子菜单事件 
    def onSeeHelp(self,event):
        pass

    def onSeeAbout(self,event):
        dlg=AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    # 文本编辑内容改变事件
    def onTextChange(self,event):
        self.is_saved=False
        self.text_content=self.text_edit.GetValue().replace('\n', '\r\n')
        if self.current_file_basename:
            self.SetTitle(self.current_file_basename+'* - '+self.app_name)
        val=self.text_edit.GetValue()
        if val:
            self.edit_menu_find.Enable(True)
            self.edit_menu_find_next.Enable(True)
        else:
            self.edit_menu_find.Enable(False)
            self.edit_menu_find_next.Enable(False)
    
    # 空闲事件
    def onIdle(self,event):
        try:
            if not self.text_edit:return none
        except wx._core.wxAssertionError:
            pass
        if wx.Clipboard().IsSupported(wx.DataFormat(wx.DF_TEXT)):
            self.edit_menu_paste.Enable(True)
        else:
            self.edit_menu_paste.Enable(False)

        if self.text_edit.GetStringSelection():
            self.edit_menu_cut.Enable(True)
            self.edit_menu_copy.Enable(True)
            self.edit_menu_del.Enable(True)
        else:
            self.edit_menu_cut.Enable(False)
            self.edit_menu_copy.Enable(False)
            self.edit_menu_del.Enable(False)
        if self.statusbar.IsShown():
            b,x,y=self.text_edit.PositionToXY(self.text_edit.GetInsertionPoint())
            self.statusbar.SetStatusText(u'  第 %d 行 , 第 %d 列'%(y+1,x+1),1)

    def onWindowResize(self,event):
        pass

    # 窗口关闭事件
    def onWindowClose(self,event):
        if self.is_saved:
            self.Destroy()
            return None
        if self.text_edit.IsModified():
            filename=self.current_file_basename or u'无标题'
            dlg=wx.MessageDialog(self,u'是否将更改保存到 '+filename+' ?',u'记事本',wx.YES_NO|wx.CANCEL)
            val=dlg.ShowModal()
            if val==wx.ID_YES:
                if self.onSaveFile(None):
                    self.Destroy()
                else:
                    event.Veto()
            elif val==wx.ID_CANCEL:
                event.Veto()
            else:
                self.Destroy()
        else:
            self.Destroy()

# 关于对话框
class AboutDialog(wx.Dialog):
    def __init__(self,parent=None):
        super(AboutDialog,self).__init__(parent,-1,u' 关于"记事本"')
        self.SetSize((380,150))
        self.CenterOnParent()
        html=wx.html.HtmlWindow(self)
        html.SetPage(u'''
            <body bgcolor="rgb(247,247,247)">
                <center>
                    <br><br>
                    版权所有 @2016 李梁 保留所有权利<br><br>
                    联系我 <b>QQ:</b>917274996 <b>电话:</b>18603732262
                </center>
            </body>
        ''')

# 转到对话框
class GotoDialog(wx.Dialog):
    def __init__(self,parent=None,rows=1,cur_row=1):
        super(GotoDialog,self).__init__(parent,-1,u'转到指定行')
        self.SetSize((300,160))
        self.CenterOnParent()
        panel=wx.Panel(self)
        btn_goto=wx.Button(panel,wx.ID_OK,u'转到')
        btn_goto.SetDefault()
        btn_cancel=wx.Button(panel,wx.ID_CANCEL,u'取消')
        label=wx.StaticText(panel,-1,u'行号(&L)')
        spin=wx.SpinCtrl(panel,min=1,max=rows,initial=cur_row+1,name='spin')

        box_bottom=wx.BoxSizer()
        main_sizer=wx.BoxSizer(wx.VERTICAL)
        box_bottom.AddStretchSpacer()
        box_bottom.Add(btn_goto)
        box_bottom.Add(btn_cancel)
        main_sizer.AddSpacer(18)
        main_sizer.Add(label,1,wx.LEFT,15)
        main_sizer.Add(spin,1,wx.EXPAND|wx.LEFT|wx.RIGHT,15)
        main_sizer.Add(box_bottom,1,wx.EXPAND|wx.TOP|wx.RIGHT,15)
        main_sizer.AddSpacer(18)
        panel.SetSizer(main_sizer)
        panel.Fit()

# 拖放目标
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self,window):
        super(MyFileDropTarget,self).__init__()
        self.window=window

    def OnDragOver(self,x, y, defResult):
        super(MyFileDropTarget,self).OnDragOver(x, y, defResult)
        return defResult

    def OnDropFiles(self,x,y,filenames):
        temp_file=unicode(filenames[0]).encode('utf-8')
        if len(filenames)>1 or not os.path.isfile(temp_file.decode('utf-8')):
            return False
        parent=self.window.Parent.Parent
        if not parent.is_saved and self.window.IsModified():
            filename=parent.current_file_basename or u'无标题'
            dlg=wx.MessageDialog(parent,u'是否将更改保存到 '+filename+' ?',u'记事本',wx.YES_NO|wx.CANCEL)
            val=dlg.ShowModal()
            if val==wx.ID_CANCEL:return False
            elif val==wx.ID_YES:
                if not parent.onSaveFile(None):
                    return False
        if self.window.LoadFile(temp_file):
            parent.current_file=temp_file
            parent.current_file_basename=os.path.basename(parent.current_file.decode('utf-8'))
            parent.SetTitle(unicode(parent.current_file_basename)+' - '+parent.app_name)
            return True

if __name__=='__main__':
    app=wx.App()
    frame=MyFrame()
    frame.Show()
    app.MainLoop()