using System.Windows;
using OBSPluginManager.ViewModels;

namespace OBSPluginManager
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            DataContext = new MainViewModel();
        }
    }
}
