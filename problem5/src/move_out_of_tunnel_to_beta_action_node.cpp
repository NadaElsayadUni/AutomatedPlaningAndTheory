#include <algorithm>
#include <iostream>
#include <memory>

#include "plansys2_executor/ActionExecutorClient.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"

using namespace std::chrono_literals;

class MoveOutOfTunnelToBetaAction : public plansys2::ActionExecutorClient
{
public:
  MoveOutOfTunnelToBetaAction()
  : plansys2::ActionExecutorClient("move_out_of_tunnel_to_beta", 250ms)
  {
    progress_ = 0.0;
  }

private:
  void do_work()
  {
    if (progress_ < 1.0) {
      progress_ += 0.04;
      send_feedback(progress_, "Move out of tunnel to beta running");
    } else {
      finish(true, 1.0, "Move out of tunnel to beta completed");

      progress_ = 0.0;
      std::cout << std::endl;
    }
    std::cout << "\r\e[K" << std::flush;
    std::cout << "move_out_of_tunnel_to_beta [" << std::min(100.0, progress_ * 100.0) << "%]  " << std::flush;
  }

  float progress_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MoveOutOfTunnelToBetaAction>();
  node->set_parameter(rclcpp::Parameter("action_name", "move_out_of_tunnel_to_beta"));
  node->trigger_transition(lifecycle_msgs::msg::Transition::TRANSITION_CONFIGURE);
  rclcpp::spin(node->get_node_base_interface());
  rclcpp::shutdown();
  return 0;
}
