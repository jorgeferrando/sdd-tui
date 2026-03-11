class SddTui < Formula
  include Language::Python::Virtualenv

  desc "TUI for Spec-Driven Development (SDD) workflow"
  homepage "https://github.com/jorgeferrando/sdd-tui"
  url "https://github.com/jorgeferrando/sdd-tui/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "SHA256_PLACEHOLDER"
  license "MIT"
  head "https://github.com/jorgeferrando/sdd-tui.git", branch: "main"

  depends_on "python@3.11"

  # To regenerate resource blocks after a dependency update:
  #   brew install poet
  #   poet sdd-tui
  resource "textual" do
    url "https://files.pythonhosted.org/packages/textual-0.70.0.tar.gz"
    sha256 "TEXTUAL_SHA256_PLACEHOLDER"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"sdd-tui", "--help"
    system bin/"sdd-setup", "--help"
    system bin/"sdd-docs", "--help"
  end
end

# ---------------------------------------------------------------------------
# HOW TO UPDATE sha256 AFTER A NEW RELEASE
# ---------------------------------------------------------------------------
#
# 1. Tag the release on GitHub:
#      git tag v0.2.0 && git push origin v0.2.0
#
# 2. Calculate the tarball sha256:
#      curl -sL https://github.com/jorgeferrando/sdd-tui/archive/refs/tags/v0.2.0.tar.gz \
#        | sha256sum
#
# 3. Update `url` version and `sha256` in this file.
#
# 4. Regenerate resource blocks (textual + dependencies):
#      brew install poet
#      poet --virtualenv sdd-tui
#    Or use `brew audit --new-formula Formula/sdd-tui.rb` to verify.
#
# 5. Commit and push — the tap auto-updates on next `brew update`.
# ---------------------------------------------------------------------------
