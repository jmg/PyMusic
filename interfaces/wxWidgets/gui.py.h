///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version Sep  8 2010)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#ifndef __gui__
#define __gui__

#include <wx/string.h>
#include <wx/textctrl.h>
#include <wx/gdicmn.h>
#include <wx/font.h>
#include <wx/colour.h>
#include <wx/settings.h>
#include <wx/sizer.h>
#include <wx/button.h>
#include <wx/tglbtn.h>
#include <wx/listctrl.h>
#include <wx/panel.h>
#include <wx/bitmap.h>
#include <wx/image.h>
#include <wx/icon.h>
#include <wx/notebook.h>
#include <wx/statusbr.h>
#include <wx/menu.h>
#include <wx/frame.h>

///////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////
/// Class wxGui
///////////////////////////////////////////////////////////////////////////////
class wxGui : public wxFrame 
{
	private:
	
	protected:
		wxTextCtrl* m_textCtrl1;
		wxTextCtrl* m_textCtrl2;
		wxButton* btPlay;
		wxButton* btStop;
		wxButton* btPause;
		wxToggleButton* tgRandom;
		wxNotebook* m_notebook1;
		wxPanel* m_panel1;
		wxListCtrl* lbSongs;
		wxPanel* m_panel2;
		wxListCtrl* lbRadios;
		wxPanel* m_panel3;
		wxTextCtrl* tbLyrics;
		wxStatusBar* m_statusBar1;
		wxMenuBar* mnBar;
		wxMenu* mnFile;
		
		// Virtual event handlers, overide them in your derived class
		virtual void btPlay_click( wxCommandEvent& event ) { event.Skip(); }
		virtual void btStop_click( wxCommandEvent& event ) { event.Skip(); }
		virtual void btPause_click( wxCommandEvent& event ) { event.Skip(); }
		virtual void tgRandom_click( wxCommandEvent& event ) { event.Skip(); }
		virtual void itAddList_click( wxCommandEvent& event ) { event.Skip(); }
		
	
	public:
		
		wxGui( wxWindow* parent, wxWindowID id = wxID_ANY, const wxString& title = wxEmptyString, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxSize( 1200,400 ), long style = wxDEFAULT_FRAME_STYLE|wxTAB_TRAVERSAL );
		~wxGui();
	
};

#endif //__gui__
