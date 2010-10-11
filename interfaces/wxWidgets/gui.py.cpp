///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version Sep  8 2010)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#include "gui.py.h"

///////////////////////////////////////////////////////////////////////////

wxGui::wxGui( wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos, const wxSize& size, long style ) : wxFrame( parent, id, title, pos, size, style )
{
	this->SetSizeHints( wxDefaultSize, wxDefaultSize );
	
	wxBoxSizer* bSizer1;
	bSizer1 = new wxBoxSizer( wxHORIZONTAL );
	
	wxBoxSizer* bSizer4;
	bSizer4 = new wxBoxSizer( wxVERTICAL );
	
	wxBoxSizer* bSizer2;
	bSizer2 = new wxBoxSizer( wxHORIZONTAL );
	
	m_textCtrl1 = new wxTextCtrl( this, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0 );
	bSizer2->Add( m_textCtrl1, 1, wxALIGN_CENTER_VERTICAL|wxALL, 5 );
	
	m_textCtrl2 = new wxTextCtrl( this, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, 0 );
	bSizer2->Add( m_textCtrl2, 0, wxALL|wxALIGN_CENTER_VERTICAL, 5 );
	
	bSizer4->Add( bSizer2, 0, wxEXPAND, 5 );
	
	wxBoxSizer* bSizer3;
	bSizer3 = new wxBoxSizer( wxHORIZONTAL );
	
	btPlay = new wxButton( this, wxID_ANY, wxT("Play"), wxDefaultPosition, wxDefaultSize, 0 );
	bSizer3->Add( btPlay, 0, wxALL, 5 );
	
	btStop = new wxButton( this, wxID_ANY, wxT("Stop"), wxDefaultPosition, wxDefaultSize, 0 );
	bSizer3->Add( btStop, 0, wxALL, 5 );
	
	btPause = new wxButton( this, wxID_ANY, wxT("Pause"), wxDefaultPosition, wxDefaultSize, 0 );
	bSizer3->Add( btPause, 0, wxALL, 5 );
	
	tgRandom = new wxToggleButton( this, wxID_ANY, wxT("Random"), wxDefaultPosition, wxDefaultSize, 0 );
	tgRandom->SetValue( true ); 
	bSizer3->Add( tgRandom, 0, wxALL, 5 );
	
	bSizer4->Add( bSizer3, 0, wxEXPAND, 5 );
	
	wxBoxSizer* bSizer6;
	bSizer6 = new wxBoxSizer( wxVERTICAL );
	
	bSizer4->Add( bSizer6, 1, wxEXPAND, 5 );
	
	bSizer1->Add( bSizer4, 1, wxEXPAND, 5 );
	
	wxBoxSizer* bSizer5;
	bSizer5 = new wxBoxSizer( wxVERTICAL );
	
	m_notebook1 = new wxNotebook( this, wxID_ANY, wxDefaultPosition, wxDefaultSize, 0 );
	m_panel1 = new wxPanel( m_notebook1, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL );
	wxBoxSizer* bSizer7;
	bSizer7 = new wxBoxSizer( wxVERTICAL );
	
	lbSongs = new wxListCtrl( m_panel1, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxLC_ICON|wxLC_LIST|wxLC_REPORT|wxLC_VIRTUAL|wxLC_VRULES|wxHSCROLL|wxRAISED_BORDER|wxVSCROLL );
	bSizer7->Add( lbSongs, 1, wxALL|wxEXPAND, 5 );
	
	m_panel1->SetSizer( bSizer7 );
	m_panel1->Layout();
	bSizer7->Fit( m_panel1 );
	m_notebook1->AddPage( m_panel1, wxT("PlayList"), true );
	m_panel2 = new wxPanel( m_notebook1, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL );
	wxBoxSizer* bSizer8;
	bSizer8 = new wxBoxSizer( wxVERTICAL );
	
	lbRadios = new wxListCtrl( m_panel2, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxLC_ICON );
	bSizer8->Add( lbRadios, 1, wxALL|wxEXPAND, 5 );
	
	m_panel2->SetSizer( bSizer8 );
	m_panel2->Layout();
	bSizer8->Fit( m_panel2 );
	m_notebook1->AddPage( m_panel2, wxT("Radios"), false );
	m_panel3 = new wxPanel( m_notebook1, wxID_ANY, wxDefaultPosition, wxDefaultSize, wxTAB_TRAVERSAL );
	wxBoxSizer* bSizer9;
	bSizer9 = new wxBoxSizer( wxVERTICAL );
	
	tbLyrics = new wxTextCtrl( m_panel3, wxID_ANY, wxEmptyString, wxDefaultPosition, wxDefaultSize, wxTE_MULTILINE );
	bSizer9->Add( tbLyrics, 1, wxALL|wxEXPAND, 5 );
	
	m_panel3->SetSizer( bSizer9 );
	m_panel3->Layout();
	bSizer9->Fit( m_panel3 );
	m_notebook1->AddPage( m_panel3, wxT("Lyrics"), false );
	
	bSizer5->Add( m_notebook1, 1, wxEXPAND | wxALL, 5 );
	
	bSizer1->Add( bSizer5, 1, wxEXPAND, 5 );
	
	this->SetSizer( bSizer1 );
	this->Layout();
	m_statusBar1 = this->CreateStatusBar( 1, wxST_SIZEGRIP, wxID_ANY );
	mnBar = new wxMenuBar( 0 );
	mnFile = new wxMenu();
	wxMenuItem* itAddList;
	itAddList = new wxMenuItem( mnFile, wxID_ANY, wxString( wxT("Add List") ) , wxEmptyString, wxITEM_NORMAL );
	mnFile->Append( itAddList );
	
	mnBar->Append( mnFile, wxT("File") ); 
	
	this->SetMenuBar( mnBar );
	
	
	this->Centre( wxBOTH );
	
	// Connect Events
	btPlay->Connect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btPlay_click ), NULL, this );
	btStop->Connect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btStop_click ), NULL, this );
	btPause->Connect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btPause_click ), NULL, this );
	tgRandom->Connect( wxEVT_COMMAND_TOGGLEBUTTON_CLICKED, wxCommandEventHandler( wxGui::tgRandom_click ), NULL, this );
	this->Connect( itAddList->GetId(), wxEVT_COMMAND_MENU_SELECTED, wxCommandEventHandler( wxGui::itAddList_click ) );
}

wxGui::~wxGui()
{
	// Disconnect Events
	btPlay->Disconnect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btPlay_click ), NULL, this );
	btStop->Disconnect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btStop_click ), NULL, this );
	btPause->Disconnect( wxEVT_COMMAND_BUTTON_CLICKED, wxCommandEventHandler( wxGui::btPause_click ), NULL, this );
	tgRandom->Disconnect( wxEVT_COMMAND_TOGGLEBUTTON_CLICKED, wxCommandEventHandler( wxGui::tgRandom_click ), NULL, this );
	this->Disconnect( wxID_ANY, wxEVT_COMMAND_MENU_SELECTED, wxCommandEventHandler( wxGui::itAddList_click ) );
	
}
