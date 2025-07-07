## Random thoughts about Codex Evaluation

### General experience with the tool / interface
* Pros
    * User interface is nice and self-explanatory. User interface is quite native to GitHub, so a GitHub user will not face difficulties
    * Creates a list of files and shows in the browser like [this](screenshots/prompt_1_response.png)
    * Addresses PR comments interactively as you see [here](screenshots/addressing_PR_comments.png)
* Cons
  * Did not find a way to edit the file before raising PR. See [this](screenshots/Cant_edit.png). What I instead had to do was to add a comment (so that the comments are audited I guess) and navigate to the left pane to let Codex address the comment in the code. Codex did address my comments as you see [here](screenshots/address_comments_before_commit.png). This is good for addressing comments that may need large changes. However, for a minor comment some way of allowing online edits would be good (with auditing capability).
  * How do we revert changes (without prompting)?
  * 

### General experience about prompt response


### Thoughts about firepower integration
* Firepower code is going to be integrated with GitHub, that makes Codex a natural choice

### Questions
* What about Agents.md file? How does one use it? The container start command logs the [following](screenshots/whats_up_with_agents_md.png).