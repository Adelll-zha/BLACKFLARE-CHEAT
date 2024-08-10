using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using Haley.WPF.Controls;

namespace BLACKFLARE_GRAPH
{
    public partial class MainWindow : Window
    {
        private const int port = 12345;
        private const string serverIP = "127.0.0.1"; // Replace with your server IP
        private TcpListener server;
        private Ellipse ellipsse;
        private SolidColorBrush selectedColor = new SolidColorBrush(Colors.Red); // Default color
        public bool active = false;
        public bool STARTED = false;

        public MainWindow()
        {
            InitializeComponent();
            colorhidder.Visibility = Visibility.Hidden;
            colorPicker.Visibility = Visibility.Hidden;
            colorhidder.Height = 0;
            colorhidder.Width = 20000;
            this.Topmost = true;
            this.AllowsTransparency = true;

            // Start the server in a separate thread to avoid blocking the UI
            System.Threading.Thread serverThread = new System.Threading.Thread(StartServer);
            serverThread.IsBackground = true;  // Set the thread as background so it terminates with the application
            serverThread.Start();

            // Handle the SizeChanged event to adjust the UI elements
            this.SizeChanged += MainWindow_SizeChanged;
        }

        private void MainWindow_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            AdjustUIElements();
        }

        private void AdjustUIElements()
        {
            // Get the current screen resolution
            double screenWidth = SystemParameters.PrimaryScreenWidth;
            double screenHeight = SystemParameters.PrimaryScreenHeight;

            // Adjust the sizes and positions of the UI elements
            canvas.Width = screenWidth;
            canvas.Height = screenHeight;
            colorhidder.Width = screenWidth;
            colorhidder.Height = screenHeight;

            if (ellipsse != null)
            {
                Canvas.SetLeft(ellipsse, (canvas.Width - ellipsse.Width) / 2);
                Canvas.SetTop(ellipsse, (canvas.Height - ellipsse.Height) / 2);
            }
        }

        private void UpdateEllipseSize(double width, double height)
        {
            // Ensure this method is called from the UI thread if updating from another thread
            Dispatcher.Invoke(() =>
            {
                canvas.Children.Clear();

                // Create and add the ellipse to the canvas
                ellipsse = new Ellipse();
                ellipsse.Width = width;
                ellipsse.Height = height;
                ellipsse.Stroke = selectedColor;

                // Centering the ellipse in the canvas
                Canvas.SetLeft(ellipsse, (canvas.Width - ellipsse.Width) / 2);
                Canvas.SetTop(ellipsse, (canvas.Height - ellipsse.Height) / 2);

                canvas.Children.Add(ellipsse); // Adding ellipse to the canvas
                dect_label.Content = "On";
                dect_label.Foreground = Brushes.Green;
            });
        }

        private void StartServer()
        {
            try
            {
                IPAddress localAddr = IPAddress.Parse(serverIP);
                server = new TcpListener(localAddr, port);
                server.Start();

                while (true)
                {
                    Console.WriteLine("Waiting for a connection...");

                    TcpClient client = server.AcceptTcpClient();
                    Console.WriteLine("Connected!");

                    NetworkStream stream = client.GetStream();

                    byte[] data = new byte[256];
                    int bytes = stream.Read(data, 0, data.Length);
                    string message = Encoding.ASCII.GetString(data, 0, bytes);
                    Console.WriteLine($"Received: {message}");

                    // Assuming message format is "width,height" e.g., "150,150"
                    string[] size = message.Split(',');
                    if (size.Length == 2 && double.TryParse(size[0], out double width) && double.TryParse(size[1], out double height))
                    {
                        UpdateEllipseSize(width, height);
                        STARTED = true;
                    }

                    client.Close();
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
            finally
            {
                server.Stop();
            }
        }

        private void blacklogo_btn_MouseDown_1(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (Stackpannel.Visibility == Visibility.Hidden)
            {
                Stackpannel.Visibility = Visibility.Visible;
            }
        }

        private void Image_MouseDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            Stackpannel.Visibility = Visibility.Hidden;
        }

        private void ColorPicker_SelectedColorChanged(object sender, RoutedPropertyChangedEventArgs<Color?> e)
        {
            if (e.NewValue.HasValue)
            {
                selectedColor = new SolidColorBrush(e.NewValue.Value);
            }
        }

        private void colorPicker_SelectedBrushChanged(object sender, RoutedEventArgs e)
        {
            if (STARTED)
            {
                selectedColor = colorPicker.SelectedBrush;
                ellipsse.Stroke = selectedColor;
            }
        }

        private void Image_MouseDown_1(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            if (!active)
            {
                colorhidder.Visibility = Visibility.Visible;
                colorPicker.Visibility = Visibility.Visible;
                colorPicker.Width = 346;
                colorPicker.Height = 530;
                colorhidder.Height = 1080;
                colorhidder.Width = 1920;

                active = true;
            }
            else
            {
                colorhidder.Visibility = Visibility.Hidden;
                colorPicker.Visibility = Visibility.Hidden;
                colorhidder.Height = 0;
                colorhidder.Width = 20000;
                colorPicker.Width = 0;
                colorPicker.Height = 0;

                active = false;
            }
        }

      
    }
}